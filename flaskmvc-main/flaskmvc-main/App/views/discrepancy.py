import csv
import io
from datetime import datetime

from flask import Blueprint, Response, render_template, jsonify, request
from flask_jwt_extended import jwt_required, current_user

from App.database import db
from App.models import MissingDevice, CheckEvent, Notification, Audit
from App.controllers.asset import get_asset
from App.controllers.room import *
from App.controllers.missingdevices import *
from App.controllers.relocation import *
from App.controllers.checkevent import *
from App.controllers.assetassignment import *
from App.controllers.audit import get_active_audit
from App.controllers.notification import create_notification
from App.controllers.notification import get_notifications_by_recipient_id


discrepancy_views = Blueprint('discrepancy_views', __name__, template_folder='../templates')


@discrepancy_views.route('/mark-room-missing', methods=['POST'])
@jwt_required()
def mark_room_missing():
    data = request.json or {}
    room_id = data.get('room_id')
    audit_id = data.get('audit_id')

    if not room_id or not audit_id:
        return jsonify({
            'success': False,
            'message': 'Room ID and Audit ID are required'
        }), 400

    mark_assets_missing_for_room(audit_id, room_id)
    return jsonify({
        'success': True,
        'message': 'Assets marked as missing for room'
    }), 200


@discrepancy_views.route('/mark-asset-found', methods=['POST'])
@jwt_required()
def mark_asset_found_route():
    data = request.json or {}
    missing_id = data.get('missing_id')
    relocation_id = data.get('relocation_id')

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
def relocate_asset_route():
    data = request.json or {}
    check_id = data.get('check_id')
    found_room_id = data.get('found_room_id')

    if not check_id or not found_room_id:
        return jsonify({
            'success': False,
            'message': 'Check ID and Found Room ID are required'
        }), 400

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
def change_asset_condition_route():
    data = request.json or {}
    check_id = data.get('check_id')
    condition = data.get('condition')

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


@discrepancy_views.route('/mark-asset-lost', methods=['POST'])
@jwt_required()
def mark_asset_lost_route():
    data = request.json or {}
    missing_id = data.get('missing_id')

    if not missing_id:
        return jsonify({
            'success': False,
            'message': 'Missing ID is required'
        }), 400

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
def get_all_rooms_api():
    rooms = get_all_rooms()
    if not rooms:
        return jsonify([]), 200
    return jsonify([room.get_json() for room in rooms]), 200


@discrepancy_views.route('/notify-discrepancy', methods=['POST'])
@jwt_required()
def notify_discrepancy():
    data = request.json or {}

    missing_asset = data.get('missing_asset', '-')
    relocated_asset = data.get('relocated_asset', '-')
    reconciliation = data.get('reconciliation', 'Pending')

    active_audit = get_active_audit()
    audit_for_notification = active_audit

    if not audit_for_notification:
        audit_for_notification = Audit.query.order_by(Audit.start_date.desc()).first()

    if not audit_for_notification:
        return jsonify({
            'success': False,
            'message': 'No audit found for notification'
        }), 400

    message = (
        f"Discrepancy notification | "
        f"Missing Asset: {missing_asset} | "
        f"Relocated Asset: {relocated_asset} | "
        f"Reconciliation: {reconciliation}"
    )

    try:
        notification = create_notification(
        audit_id=audit_for_notification.audit_id,
        recipient_id=current_user.user_id,
        message=message
    )
        
        db.session.add(notification)
        db.session.commit()

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