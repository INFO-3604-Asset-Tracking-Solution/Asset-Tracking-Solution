import csv
import io
from datetime import datetime

from flask import Blueprint, Response, render_template, jsonify, request
from flask_jwt_extended import jwt_required, current_user

from App.database import db
from App.controllers.asset import (
    get_asset,
    get_assets_by_status,
    get_discrepant_assets,
    mark_asset_lost,
    mark_asset_found,
    update_asset_location,
    bulk_mark_assets_found, # Import new function
    bulk_relocate_assets    # Import new function
)
from App.controllers.room import get_room, get_all_rooms
from datetime import datetime
from App.controllers.scanevent import add_scan_event
from App.controllers.permissions import role_required  # Added for RBAC

discrepancy_views = Blueprint('discrepancy_views', __name__, template_folder='../templates')

# --- Existing routes remain the same ---
@discrepancy_views.route('/discrepancy-report', methods=['GET'])
@jwt_required()
@role_required('Auditor')  # Only auditors can view discrepancy page
def discrepancy_report_page():
    # Default without loading data in template (will be loaded via API)
    return render_template('discrepancy.html')

@discrepancy_views.route('/mark-room-missing', methods=['POST'])
@jwt_required()
@role_required('Auditor')  # Only auditors can fetch discrepancies
def get_discrepancies():
    """API endpoint to get all discrepancy assets"""
    discrepancies = get_discrepant_assets()

    # Enrich with room information
    for asset in discrepancies:
        # Get expected room name (if available)
        if asset.get('room_id'):
            room = get_room(asset['room_id'])
            if room:
                asset['room_name'] = room.room_name
            else:
                asset['room_name'] = f"Room {asset['room_id']}"
        else:
            asset['room_name'] = "Unknown"

        # Get last located room name (if available)
        if asset.get('last_located') and asset['last_located'] != asset['room_id']:
            last_room = get_room(asset['last_located'])
            if last_room:
                asset['last_located_name'] = last_room.room_name
            else:
                asset['last_located_name'] = f"Room {asset['last_located']}"

    return jsonify(discrepancies)

@discrepancy_views.route('/api/rooms/all', methods=['GET'])
@jwt_required()
@role_required(['Manager', 'Administrator'])  # Only managers/admins can fetch rooms for relocation
def get_all_rooms_json():
    """API endpoint to get all rooms for relocation"""
    rooms = get_all_rooms()
    if not rooms:
        return jsonify([])
    rooms_json = [room.get_json() for room in rooms]
    return jsonify(rooms_json)

@discrepancy_views.route('/api/discrepancies/missing', methods=['GET'])
@jwt_required()
@role_required('Auditor')  # Only auditors can fetch missing assets
def get_missing():
    """API endpoint to get missing assets"""
    missing = get_assets_by_status("Missing")
    return jsonify(missing)

@discrepancy_views.route('/api/discrepancies/misplaced', methods=['GET'])
@jwt_required()
@role_required('Auditor')  # Only auditors can fetch misplaced assets
def get_misplaced():
    """API endpoint to get misplaced assets"""
    misplaced = get_assets_by_status("Misplaced")
    return jsonify(misplaced)

@discrepancy_views.route('/mark-asset-found', methods=['POST'])
@jwt_required()
@role_required(['Manager', 'Administrator'])  # Managers/admins can mark assets as lost
def mark_asset_as_lost(asset_id):
    """API endpoint to mark an asset as lost"""
    asset = mark_asset_lost(asset_id, current_user.id)

    if not missing_id or not relocation_id:
        return jsonify({
            'success': False,
            'message': 'Missing ID and Relocation ID are required'
        }), 400

    result = mark_asset_found(missing_id, relocation_id)
    if result:
        return jsonify({
            'success': True,
            'message': 'Asset marked as found'
        }), 200

    return jsonify({
        'success': False,
        'message': 'Failed to mark asset as found'
    }), 500


@discrepancy_views.route('/relocate-asset', methods=['POST'])
@jwt_required()
@role_required(['Manager', 'Administrator'])  # Managers/admins can mark assets as found
def mark_asset_as_found(asset_id):
    """API endpoint to mark an asset as found"""
    # Return to room is always true for this endpoint
    asset = mark_asset_found(asset_id, current_user.id, return_to_room=True)

    result = create_relocation(check_id, found_room_id)
    if result:
        return jsonify({
            'success': True,
            'message': 'Relocation created',
            'relocation_id': result.relocation_id
        }), 201

    return jsonify({
        'success': False,
        'message': 'Failed to create relocation'
    }), 500


@discrepancy_views.route('/change-asset-condition', methods=['POST'])
@jwt_required()
@role_required(['Manager', 'Administrator'])  # Managers/admins can relocate assets
def relocate_asset(asset_id):
    """API endpoint to mark an asset as found and relocate/reassign it (single item)"""
    data = request.json

    if not check_id or not condition:
        return jsonify({
            'success': False,
            'message': 'Check ID and Condition are required'
        }), 400

    result = update_check_event_condition(check_id, condition)
    if result:
        return jsonify({
            'success': True,
            'message': 'Asset condition updated'
        }), 200

    return jsonify({
        'success': False,
        'message': 'Failed to update asset condition'
    }), 500


@discrepancy_views.route('/mark-asset-relocated', methods=['POST'])
@jwt_required()
def mark_asset_relocated_route():
    data = request.json or {}
    relocation_id = data.get('relocation_id')
    item_relocated_room_id = data.get('item_relocated_room_id')

    if not relocation_id or not item_relocated_room_id:
        return jsonify({
            'success': False,
            'message': 'Relocation ID and Item Relocated Room ID are required'
        }), 400

    result = update_relocation(relocation_id, item_relocated_room_id)
    if result:
        return jsonify({
            'success': True,
            'message': 'Asset marked as relocated'
        }), 200

    return jsonify({
        'success': False,
        'message': 'Failed to mark asset as relocated'
    }), 500


@discrepancy_views.route('/reconcile-discrepancy', methods=['POST'])
@jwt_required()
def reconcile_discrepancy_route():
    data = request.json or {}
    asset_id = data.get('asset_id')
    new_room_id = data.get('new_room_id')
    new_condition = data.get('new_condition')

    if not asset_id or not new_room_id or not new_condition:
        return jsonify({
            'success': False,
            'message': 'Asset ID, New Room ID, and New Condition are required'
        }), 400

    result = reconcile_discrepancy(asset_id, new_room_id, new_condition)
    if result:
        return jsonify({
            'success': True,
            'message': 'Discrepancy reconciled'
        }), 200

    return jsonify({
        'success': False,
        'message': 'Failed to reconcile discrepancy'
    }), 500

@discrepancy_views.route('/api/assets/bulk-mark-found', methods=['POST'])
@jwt_required()
@role_required(['Manager', 'Administrator'])  # Managers/admins can bulk mark assets found
def bulk_mark_found_endpoint():
    """API endpoint for bulk marking assets as found"""
    data = request.json
    if not data or 'assetIds' not in data or not isinstance(data['assetIds'], list):
        return jsonify({'success': False, 'message': 'Invalid input. "assetIds" (list) required.'}), 400

    asset_ids = data['assetIds']
    notes = data.get('notes', '')
    # Get the flag for skipping failed scan events
    skip_failed_scan_events = data.get('skipFailedScanEvents', False)
    
    processed_count, error_count, errors = bulk_mark_assets_found(
        asset_ids, 
        current_user.id, 
        notes, 
        skip_failed_scan_events
    )

    result = mark_asset_lost(missing_id)
    if result:
        return jsonify({
            'success': True,
            'message': 'Asset marked as lost'
        }), 200

    return jsonify({
        'success': False,
        'message': 'Failed to mark asset as lost'
    }), 500


@discrepancy_views.route('/discrepancy-report', methods=['GET'])
@jwt_required()
def discrepancy_report_page():
    return render_template('discrepancy.html')


def build_discrepancy_rows():
    rows = []

    # Missing assets not yet found
    missing_records = MissingDevice.query.filter_by(found_relocation_id=None).all()
    for missing in missing_records:
        assignment = get_asset_assignment_by_id(missing.assignment_id)
        if not assignment:
            continue

        asset = get_asset(assignment.asset_id)
        asset_name = asset.description if asset and asset.description else assignment.asset_id

        rows.append({
            'missing_asset': asset_name,
            'relocated_asset': '-',
            'reconciliation': 'Pending',
            'action': 'Notify',
            'missing_id': missing.missing_id,
            'relocation_id': None,
            'check_id': None,
            'asset_id': assignment.asset_id
        })

    # Relocated assets
    relocations = get_all_relocations()
    for relocation in relocations:
        check = CheckEvent.query.get(relocation.check_id)
        if not check:
            continue

        asset = get_asset(check.asset_id)
        asset_name = asset.description if asset and asset.description else check.asset_id

        reconciliation_status = 'Resolved' if relocation.new_check_event_id else 'In Review'

        rows.append({
            'missing_asset': '-',
            'relocated_asset': asset_name,
            'reconciliation': reconciliation_status,
            'action': 'Notify',
            'missing_id': None,
            'relocation_id': relocation.relocation_id,
            'check_id': relocation.check_id,
            'asset_id': check.asset_id
        })

    return rows


@discrepancy_views.route('/api/discrepancies', methods=['GET'])
@jwt_required()
def get_discrepancies():
    try:
        rows = build_discrepancy_rows()
        return jsonify(rows), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to load discrepancies: {str(e)}'
        }), 500


@discrepancy_views.route('/api/rooms/all', methods=['GET'])
@jwt_required()
@role_required(['Manager', 'Administrator'])  # Managers/admins can bulk relocate assets
def bulk_relocate_endpoint():
    """API endpoint for bulk relocating assets"""
    data = request.json
    if not data or \
       'assetIds' not in data or not isinstance(data['assetIds'], list) or \
       'roomId' not in data:
        return jsonify({'success': False, 'message': 'Invalid input. "assetIds" (list) and "roomId" required.'}), 400

    asset_ids = data['assetIds']
    new_room_id = data['roomId']
    notes = data.get('notes', '') # Optional notes for the bulk action

    processed_count, error_count, errors = bulk_relocate_assets(asset_ids, new_room_id, current_user.id, notes)

    if error_count == 0:
        room = get_room(new_room_id)
        room_name = room.room_name if room else f"Room {new_room_id}"
        return jsonify({
            'success': True,
            'message': 'Notification created successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to create notification: {str(e)}'
        }), 500


@discrepancy_views.route('/api/discrepancies/download', methods=['GET'])
@jwt_required()
@role_required(['Manager', 'Administrator', 'Auditor'])  # All roles can download discrepancy CSV
def download_discrepancies():
    try:
        rows = build_discrepancy_rows()

        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(['Discrepancy Report'])
        writer.writerow(['Generated By', current_user.username])
        writer.writerow(['Date & Time', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        writer.writerow([])

        writer.writerow(['Missing Assets', 'Relocated Assets', 'Reconciliation', 'Action'])

        for row in rows:
            writer.writerow([
                row.get('missing_asset', ''),
                row.get('relocated_asset', ''),
                row.get('reconciliation', ''),
                row.get('action', '')
            ])

        output.seek(0)
        filename = f"discrepancy_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"'
            }
        )
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to export discrepancies: {str(e)}'
        }), 500
    
@discrepancy_views.route('/api/my-notifications', methods=['GET'])
@jwt_required()
def get_my_notifications():
    notifications = get_notifications_by_recipient_id(current_user.user_id)
    return jsonify([notification.get_json() for notification in notifications]), 200