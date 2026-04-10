import csv
import io
from datetime import datetime
 

from flask import Blueprint, Response, jsonify, render_template, request
from flask_jwt_extended import current_user, jwt_required, get_jwt_identity

from App.database import db
from App.controllers.permissions import role_required
from App.controllers.room import get_all_rooms_json, get_room
from App.controllers.relocation import *
from App.controllers.user import get_user

from App.controllers.missingdevices import mark_asset_found, mark_asset_lost
from App.controllers.checkevent import update_check_event_condition
from App.controllers.assetassignment import get_current_asset_assignment, reconcile_discrepancy
from App.controllers.notification import create_notification, get_notifications_by_recipient_id
from App.controllers.audit import get_active_audit
from App.models.missingdevices import MissingDevice
from App.models.checkevent import CheckEvent
from App.models.assetassignment import AssetAssignment
from App.models.asset import Asset
from App.models.room import Room


discrepancy_views = Blueprint('discrepancy_views', __name__, template_folder='../templates')
print("DEBUG: Discrepancy views loaded with enrichment logic.")


def _build_discrepancy_rows(audit_id=None):
    """
    Unified discrepancy row builder used by UI + CSV.
    """
    rows = []

    # Missing records (open only)
    missing_query = MissingDevice.query.filter_by(found_relocation_id=None)
    if audit_id:
        missing_query = missing_query.filter_by(audit_id=audit_id)
    missing_records = missing_query.all()
    for missing in missing_records:
        assignment = AssetAssignment.query.get(missing.assignment_id)
        asset_id = assignment.asset_id if assignment else None
        if not asset_id:
            continue
        
        asset = Asset.query.get(asset_id)

        rows.append({
            "row_type": "missing",
            "asset_id": asset_id,
            "asset_description": asset.description if asset else "No description",
            "missing": asset_id,
            "relocated": "-",
            "reconciliation": "Pending",
            "missing_id": missing.missing_id,
            "relocation_id": None,
            "check_id": None,
            "can_mark_lost": True,
            "can_mark_relocated": False
        })

    # Relocations
    relocations = get_all_relocations() or []
    for relocation in relocations:
        check = CheckEvent.query.get(relocation.check_id)
        if not check:
            continue
        if audit_id and check.audit_id != audit_id:
            continue

        asset_id = check.asset_id
        asset = Asset.query.get(asset_id)
        
        # Room info for modal UI
        assignment = AssetAssignment.query.filter_by(asset_id=asset_id, return_date=None).first()
        expected_room = Room.query.get(assignment.room_id) if assignment else None
        found_room = Room.query.get(relocation.found_in_id)
        
        reconciliation_status = "Resolved" if relocation.new_check_event_id else "Room Mismatch"

        rows.append({
            "row_type": "relocation",
            "asset_id": asset_id,
            "asset_description": asset.description if asset else "No description",
            "expected_room_name": expected_room.room_name if expected_room else "Unassigned",
            "found_room_name": found_room.room_name if found_room else "Unknown",
            "found_room_id": found_room.room_id if found_room else None,
            "missing": "-",
            "relocated": asset_id,
            "reconciliation": reconciliation_status,
            "missing_id": None,
            "relocation_id": relocation.relocation_id,
            "check_id": relocation.check_id,
            "can_mark_lost": False,
            "can_mark_relocated": relocation.new_check_event_id is None
        })

    return rows


@discrepancy_views.route('/discrepancy-report', methods=['GET'])
@jwt_required()
def discrepancy_report_page():
    return render_template('discrepancy.html')


@discrepancy_views.route('/api/discrepancies', methods=['GET'])
@jwt_required()
def get_discrepancies_api():
    try:
        active_audit = get_active_audit()
        rows = _build_discrepancy_rows(active_audit.audit_id) if active_audit else []
        return jsonify(rows), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Failed to load discrepancies: {str(e)}"
        }), 500


@discrepancy_views.route('/api/discrepancies/missing', methods=['GET'])
@jwt_required()
@role_required(['Manager', 'Administrator', 'Auditor'])
def get_missing_api():
    active_audit = get_active_audit()
    rows = [r for r in _build_discrepancy_rows(active_audit.audit_id) if r["missing"] != "-"] if active_audit else []
    return jsonify(rows), 200


@discrepancy_views.route('/api/discrepancies/misplaced', methods=['GET'])
@jwt_required()
@role_required(['Manager', 'Administrator', 'Auditor'])
def get_misplaced_api():
    active_audit = get_active_audit()
    rows = [r for r in _build_discrepancy_rows(active_audit.audit_id) if r["relocated"] != "-"] if active_audit else []
    return jsonify(rows), 200


@discrepancy_views.route('/mark-asset-found', methods=['POST'])
@jwt_required()
@role_required(['Manager', 'Administrator'])
def mark_asset_as_found_route():
    data = request.json or {}
    missing_id = data.get("missing_id")
    relocation_id = data.get("relocation_id")

    if not missing_id or not relocation_id:
        return jsonify({
            "success": False,
            "message": "Missing ID and Relocation ID are required"
        }), 400

    result = mark_asset_found(missing_id, relocation_id)
    if result:
        return jsonify({
            "success": True,
            "message": "Asset marked as found"
        }), 200

    return jsonify({
        "success": False,
        "message": "Failed to mark asset as found"
    }), 500


@discrepancy_views.route('/mark-asset-lost', methods=['POST'])
@jwt_required()
@role_required(['Manager', 'Administrator'])
def mark_asset_as_lost_route():
    data = request.json or {}
    missing_id = data.get("missing_id")

    if not missing_id:
        return jsonify({
            "success": False,
            "message": "Missing ID is required"
        }), 400

    result = mark_asset_lost(missing_id)
    if result:
        return jsonify({
            "success": True,
            "message": "Asset marked as lost"
        }), 200

    return jsonify({
        "success": False,
        "message": "Failed to mark asset as lost"
    }), 500


@discrepancy_views.route('/relocate-asset', methods=['POST'])
@jwt_required()
@role_required(['Manager', 'Administrator'])
def relocate_asset_route():
    data = request.json or {}
    check_id = data.get("check_id")
    found_room_id = data.get("found_room_id")

    if not check_id or not found_room_id:
        return jsonify({
            "success": False,
            "message": "Check ID and Found Room ID are required"
        }), 400

    result = create_relocation(check_id, found_room_id)
    if result:
        return jsonify({
            "success": True,
            "message": "Relocation created",
            "relocation_id": result.relocation_id
        }), 201

    return jsonify({
        "success": False,
        "message": "Failed to create relocation"
    }), 500


@discrepancy_views.route('/change-asset-condition', methods=['POST'])
@jwt_required()
@role_required(['Manager', 'Administrator'])
def change_asset_condition_route():
    data = request.json or {}
    check_id = data.get("check_id")
    condition = data.get("condition")

    if not check_id or not condition:
        return jsonify({
            "success": False,
            "message": "Check ID and Condition are required"
        }), 400

    result = update_check_event_condition(check_id, condition)
    if result:
        return jsonify({
            "success": True,
            "message": "Asset condition updated"
        }), 200

    return jsonify({
        "success": False,
        "message": "Failed to update asset condition"
    }), 500


@discrepancy_views.route('/mark-asset-relocated', methods=['POST'])
@jwt_required()
@role_required(['Manager', 'Administrator'])
def mark_asset_relocated_route():
    data = request.json or {}
    relocation_id = data.get("relocation_id")
    item_relocated_room_id = data.get("item_relocated_room_id")

    if not relocation_id or not item_relocated_room_id:
        return jsonify({
            "success": False,
            "message": "Relocation ID and Item Relocated Room ID are required"
        }), 400

    result = update_relocation(relocation_id, item_relocated_room_id)
    if result:
        return jsonify({
            "success": True,
            "message": "Asset marked as relocated"
        }), 200

    return jsonify({
        "success": False,
        "message": "Failed to mark asset as relocated"
    }), 500


@discrepancy_views.route('/reconcile-discrepancy', methods=['POST'])
@jwt_required()
@role_required(['Manager', 'Administrator'])
def reconcile_discrepancy_route():
    data = request.json or {}
    asset_id = data.get("asset_id")
    new_room_id = data.get("new_room_id")
    new_condition = data.get("new_condition")

    if not asset_id or not new_room_id or not new_condition:
        return jsonify({
            "success": False,
            "message": "Asset ID, New Room ID, and New Condition are required"
        }), 400

    result = reconcile_discrepancy(asset_id, new_room_id, new_condition)
    if result:
        return jsonify({
            "success": True,
            "message": "Discrepancy reconciled"
        }), 200

    return jsonify({
        "success": False,
        "message": "Failed to reconcile discrepancy"
    }), 500


@discrepancy_views.route('/api/assets/bulk-mark-found', methods=['POST'])
@jwt_required()
@role_required(['Manager', 'Administrator'])
def bulk_mark_found_endpoint():
    """
    Expects:
    {
      "pairs": [{"missing_id": 1, "relocation_id": "abc123"}, ...]
    }
    """
    data = request.json or {}
    pairs = data.get("pairs", [])

    if not isinstance(pairs, list) or len(pairs) == 0:
        return jsonify({
            "success": False,
            "message": 'Invalid input. "pairs" (non-empty list) required.'
        }), 400

    processed_count = 0
    error_count = 0
    errors = []

    for pair in pairs:
        missing_id = pair.get("missing_id")
        relocation_id = pair.get("relocation_id")

        if not missing_id or not relocation_id:
            error_count += 1
            errors.append("Each pair requires missing_id and relocation_id")
            continue

        result = mark_asset_found(missing_id, relocation_id)
        if result:
            processed_count += 1
        else:
            error_count += 1
            errors.append(f"Failed for missing_id={missing_id}, relocation_id={relocation_id}")

    return jsonify({
        "success": processed_count > 0,
        "processed_count": processed_count,
        "error_count": error_count,
        "errors": errors[:10]
    }), (200 if processed_count > 0 else 500)


@discrepancy_views.route('/api/bulk-relocations/all', methods=['POST'])
@jwt_required()
@role_required(['Manager', 'Administrator'])
def bulk_relocate_endpoint():
    """
    Expects:
    {
      "assetIds": ["A-xxxx", ...],
      "roomId": 12
    }
    """
    data = request.json or {}
    asset_ids = data.get("assetIds")
    new_room_id = data.get("roomId")

    if not isinstance(asset_ids, list) or not new_room_id:
        return jsonify({
            "success": False,
            "message": 'Invalid input. "assetIds" (list) and "roomId" required.'
        }), 400

    processed_count = 0
    error_count = 0
    errors = []

    for asset_id in asset_ids:
        assignment = get_current_asset_assignment(asset_id)
        if not assignment:
            error_count += 1
            errors.append(f"No active assignment for asset {asset_id}")
            continue

        result = reconcile_discrepancy(asset_id, new_room_id, assignment.condition)
        if result:
            processed_count += 1
        else:
            error_count += 1
            errors.append(f"Failed to relocate asset {asset_id}")

    room = get_room(new_room_id)
    room_name = room.room_name if room else f"Room {new_room_id}"

    return jsonify({
        "success": processed_count > 0,
        "message": f"Relocated {processed_count} assets to {room_name}" if processed_count > 0 else "Bulk relocation failed",
        "processed_count": processed_count,
        "error_count": error_count,
        "errors": errors[:10]
    }), (200 if processed_count > 0 else 500)


@discrepancy_views.route('/api/rooms/all', methods=['GET'])
@jwt_required()
@role_required(['Manager', 'Administrator', 'Auditor'])
def get_all_rooms_for_discrepancy():
    """API endpoint to get all rooms for relocation."""
    return jsonify(get_all_rooms_json()), 200


@discrepancy_views.route('/api/discrepancies/download', methods=['GET'])
@jwt_required()
@role_required(['Manager', 'Administrator', 'Auditor'])
def download_discrepancies():
    try:
        active_audit = get_active_audit()
        rows = _build_discrepancy_rows(active_audit.audit_id) if active_audit else []

        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(["Discrepancy Report"])
        writer.writerow(["Generated By", current_user.username])
        writer.writerow(["Date & Time", datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        writer.writerow([])
        writer.writerow(["Missing Assets", "Relocated Assets", "Reconciliation"])

        for row in rows:
            writer.writerow([
                row.get("missing", "-"),
                row.get("relocated", "-"),
                row.get("reconciliation", "Pending")
            ])

        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={"Content-Disposition": "attachment;filename=discrepancy_report.csv"}
        )
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Failed to export discrepancies: {str(e)}"
        }), 500


@discrepancy_views.route('/notify-discrepancy', methods=['POST'])
@jwt_required()
def notify_discrepancy():
    data = request.json or {}

    missing_asset = data.get('missing_asset', '-')
    relocated_asset = data.get('relocated_asset', '-')
    reconciliation = data.get('reconciliation', 'Pending')

    active_audit = get_active_audit()
    if not active_audit:
        return jsonify({
            'success': False,
            'message': 'No active audit found. Start an audit to create discrepancy notifications.'
        }), 400

    message = (
        f"Discrepancy update | Missing: {missing_asset} | "
        f"Relocated: {relocated_asset} | Reconciliation: {reconciliation}"
    )

    notification = create_notification(active_audit.audit_id, current_user.user_id, message)
    if not notification:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to create notification'
        }), 500

    return jsonify({
        'success': True,
        'message': 'Notification created successfully',
        'notification': notification.get_json()
    }), 200


@discrepancy_views.route('/api/my-notifications', methods=['GET'])
@jwt_required()
def get_my_notifications():
    notifications = get_notifications_by_recipient_id(current_user.user_id)
    return jsonify([notification.get_json() for notification in notifications]), 200

@discrepancy_views.route('/api/relocation/resolve', methods=['POST'])
@jwt_required()
def resolve_relocation_extended_route():
    user_id = get_jwt_identity()
    user = get_user(user_id)
    
    if user.role not in ['Manager', 'Administrator']:
        return jsonify({"message": "Unauthorized"}), 403

    data = request.json or {}
    relocation_id = data.get("relocation_id")
    choice = data.get("choice")
    new_room_id = data.get("new_room_id")

    if not relocation_id or not choice:
        return jsonify({"message": "Missing required fields"}), 400

    result = resolve_relocation_extended(relocation_id, choice, new_room_id)
    if result:
        return jsonify({"message": f"Relocation resolved as {choice}", "success": True}), 200
    
    return jsonify({"message": "Failed to resolve relocation"}), 500