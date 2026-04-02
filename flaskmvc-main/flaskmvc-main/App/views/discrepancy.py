import csv
import io
from datetime import datetime

from flask import Blueprint, Response, render_template, jsonify, request
from flask_jwt_extended import jwt_required, current_user

from App.database import db
from App.controllers.asset import *
from App.controllers.room import *
from App.controllers.permissions import *

discrepancy_views = Blueprint('discrepancy_views', __name__, template_folder='../templates')

# --- Existing routes remain the same ---

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

# --- Existing routes remain the same ---
# @discrepancy_views.route('/discrepancy-report', methods=['GET'])
# @jwt_required()
# def discrepancy_report_page():
#     # Default without loading data in template (will be loaded via API)
#     return render_template('discrepancy.html')

# @discrepancy_views.route('/api/discrepancies', methods=['GET'])
# @jwt_required()
# def get_discrepancies():
#     """API endpoint to get all discrepancy assets"""
#     discrepancies = get_discrepant_assets()

#     # Enrich with room information
#     for asset in discrepancies:
#         # Get expected room name (if available)
#         if asset.get('room_id'):
#             room = get_room(asset['room_id'])
#             if room:
#                 asset['room_name'] = room.room_name
#             else:
#                 asset['room_name'] = f"Room {asset['room_id']}"
#         else:
#             asset['room_name'] = "Unknown"

#         # Get last located room name (if available)
#         if asset.get('last_located') and asset['last_located'] != asset['room_id']:
#             last_room = get_room(asset['last_located'])
#             if last_room:
#                 asset['last_located_name'] = last_room.room_name
#             else:
#                 asset['last_located_name'] = f"Room {asset['last_located']}"

#     return jsonify(discrepancies)

@discrepancy_views.route('/api/rooms/all', methods=['GET'])
@jwt_required()
def get_all_rooms_json():
    """API endpoint to get all rooms for relocation"""
    rooms = get_all_rooms()
    if not rooms:
        return jsonify([])
    rooms_json = [room.get_json() for room in rooms]
    return jsonify(rooms_json)

# @discrepancy_views.route('/api/discrepancies/missing', methods=['GET'])
# @jwt_required()
# def get_missing():
#     """API endpoint to get missing assets"""
#     missing = get_assets_by_status("Missing")
#     return jsonify(missing)

# @discrepancy_views.route('/api/discrepancies/misplaced', methods=['GET'])
# @jwt_required()
# def get_misplaced():
#     """API endpoint to get misplaced assets"""
#     misplaced = get_assets_by_status("Misplaced")
#     return jsonify(misplaced)

# @discrepancy_views.route('/api/asset/<asset_id>/mark-lost', methods=['POST'])
# @jwt_required()
# def mark_asset_as_lost(asset_id):
#     """API endpoint to mark an asset as lost"""
#     asset = mark_asset_lost(asset_id, current_user.id)

#     if not asset:
#         return jsonify({'success': False, 'message': 'Failed to mark asset as lost. Asset not found or error occurred.'}), 404

#     return jsonify({
#         'success': True,
#         'message': 'Asset successfully marked as lost',
#         'asset': asset.get_json()
#     })

# @discrepancy_views.route('/api/asset/<asset_id>/mark-found', methods=['POST'])
# @jwt_required()
# def mark_asset_as_found(asset_id):
#     """API endpoint to mark an asset as found"""
#     # Return to room is always true for this endpoint
#     asset = mark_asset_found(asset_id, current_user.id, return_to_room=True)

#     if not asset:
#         return jsonify({'success': False, 'message': 'Failed to mark asset as found. Asset not found or error occurred.'}), 404

#     return jsonify({
#         'success': True,
#         'message': 'Asset successfully marked as found and returned to its assigned room',
#         'asset': asset.get_json()
#     })

# @discrepancy_views.route('/api/asset/<asset_id>/relocate', methods=['POST'])
# @jwt_required()
# def relocate_asset(asset_id):
#     """API endpoint to mark an asset as found and relocate/reassign it (single item)"""
#     data = request.json

#     if not data or 'roomId' not in data:
#         return jsonify({'success': False, 'message': 'Room ID is required'}), 400

#     new_room_id = data['roomId']
#     user_notes = data.get('notes', '')  # Get optional notes

#     # Get the asset directly
#     asset = get_asset(asset_id)
#     if not asset:
#         return jsonify({'success': False, 'message': 'Asset not found'}), 404

#     # Store old status and location for changelog
#     old_status = asset.status
#     old_location = asset.room_id

#     # Update both room_id AND last_located in one operation
#     asset.last_located = new_room_id
#     asset.room_id = new_room_id
#     asset.status = "Good"
#     asset.last_update = datetime.now()

#     try:
#         # Get room names for better context in notes
#         old_room_name = get_room(old_location).room_name if get_room(old_location) else f"Room {old_location}"
#         new_room_name = get_room(new_room_id).room_name if get_room(new_room_id) else f"Room {new_room_id}"

#         # Create the base notes about the relocation/reassignment
#         if old_location == new_room_id:
#             system_notes = f"Asset reassigned to its current location ({new_room_name})."
#         else:
#              # Check if it was Missing or Misplaced to tailor the message
#             if old_status == "Missing":
#                  system_notes = f"Asset marked as Found and relocated/reassigned from {old_room_name} to {new_room_name}."
#             else: # Misplaced or other
#                  system_notes = f"Asset location record updated. Reassigned from {old_room_name} to {new_room_name}."

#         # Add status change information
#         system_notes += f" Previous status: {old_status}."

#         # Append user notes if provided
#         if user_notes:
#             notes = f"{system_notes} \n User note: {user_notes}"
#         else:
#             notes = system_notes

#         # Create a single scan event using the existing controller
#         add_scan_event(
#             asset_id=asset_id,
#             user_id=current_user.id,
#             room_id=new_room_id,
#             status="Good",
#             notes=notes
#         )

#         # Commit all changes at once
#         db.session.commit()

#         # Get room name for the response message
#         room = get_room(new_room_id)
#         room_name = room.room_name if room else f"Room {new_room_id}"

#         return jsonify({
#             'success': True,
#             'message': f'Asset successfully updated and assigned to {room_name}',
#             'asset': asset.get_json()
#         })
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({'success': False, 'message': f'Error updating asset: {str(e)}'}), 500



# @discrepancy_views.route('/api/assets/bulk-mark-found', methods=['POST'])
# @jwt_required()
# def bulk_mark_found_endpoint():
#     """API endpoint for bulk marking assets as found"""
#     data = request.json
#     if not data or 'assetIds' not in data or not isinstance(data['assetIds'], list):
#         return jsonify({'success': False, 'message': 'Invalid input. "assetIds" (list) required.'}), 400

#     asset_ids = data['assetIds']
#     notes = data.get('notes', '')
#     # Get the flag for skipping failed scan events
#     skip_failed_scan_events = data.get('skipFailedScanEvents', False)
    
#     processed_count, error_count, errors = bulk_mark_assets_found(
#         asset_ids, 
#         current_user.id, 
#         notes, 
#         skip_failed_scan_events
#     )

#     # Return success if any assets were processed, even with some errors
#     if processed_count > 0:
#         return jsonify({
#             'success': True,
#             'message': f'{processed_count} asset(s) marked as found.',
#             'processed_count': processed_count,
#             'error_count': error_count,
#             'errors': errors[:10] if errors else []  # Limit errors in response
#         })
#     else:
#         return jsonify({
#             'success': False,
#             'message': f'Failed to mark assets as found. See errors for details.',
#             'processed_count': processed_count,
#             'error_count': error_count,
#             'errors': errors[:10] # Limit errors in response
#         }), 500

# @discrepancy_views.route('/api/assets/bulk-relocate', methods=['POST'])
# @jwt_required()
# def bulk_relocate_endpoint():
#     """API endpoint for bulk relocating assets"""
#     data = request.json
#     if not data or \
#        'assetIds' not in data or not isinstance(data['assetIds'], list) or \
#        'roomId' not in data:
#         return jsonify({'success': False, 'message': 'Invalid input. "assetIds" (list) and "roomId" required.'}), 400

#     asset_ids = data['assetIds']
#     new_room_id = data['roomId']
#     notes = data.get('notes', '') # Optional notes for the bulk action

#     processed_count, error_count, errors = bulk_relocate_assets(asset_ids, new_room_id, current_user.id, notes)

#     if error_count == 0:
#         room = get_room(new_room_id)
#         room_name = room.room_name if room else f"Room {new_room_id}"
#         return jsonify({
#             'success': True,
#             'message': f'{processed_count} asset(s) marked as found and relocated to {room_name}.',
#             'processed_count': processed_count
#         })
#     else:
#         return jsonify({
#             'success': False,
#             'message': f'Processed {processed_count} asset(s), but {error_count} failed. See errors for details.',
#             'processed_count': processed_count,
#             'error_count': error_count,
#             'errors': errors[:10] # Limit errors in response
#         }), 500
        
# @discrepancy_views.route('/api/discrepancies/download', methods=['GET'])
# @jwt_required()
# def download_discrepancies():
#     """API endpoint to download discrepancies as CSV"""
#     filter_type = request.args.get('filter', 'all')
    
#     # Get the appropriate discrepancies based on filter
#     if filter_type == 'all':
#         discrepancies = get_discrepant_assets()
#     elif filter_type == 'missing':
#         discrepancies = get_assets_by_status("Missing")
#     elif filter_type == 'misplaced':
#         discrepancies = get_assets_by_status("Misplaced")
#     else:
#         discrepancies = get_discrepant_assets()
    
#     # Enrich with room information (same as in get_discrepancies endpoint)
#     for asset in discrepancies:
#         # Get expected room name (if available)
#         if asset.get('room_id'):
#             room = get_room(asset['room_id'])
#             if room:
#                 asset['room_name'] = room.room_name
#             else:
#                 asset['room_name'] = f"Room {asset['room_id']}"
#         else:
#             asset['room_name'] = "Unknown"

#         # Get last located room name (if available)
#         if asset.get('last_located') and asset['last_located'] != asset['room_id']:
#             last_room = get_room(asset['last_located'])
#             if last_room:
#                 asset['last_located_name'] = last_room.room_name
#             else:
#                 asset['last_located_name'] = f"Room {asset['last_located']}"
#         else:
#             asset['last_located_name'] = asset.get('room_name', 'Unknown')
    
#     # Create in-memory CSV file
#     output = io.StringIO()
#     writer = csv.writer(output)
    
#     # Add a header row with audit information
#     writer.writerow(['Discrepancy Report'])
#     writer.writerow(['Generated By', current_user.username])
#     writer.writerow(['Date & Time', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
#     writer.writerow(['Filter', filter_type.capitalize()])
#     writer.writerow([]) # Empty row as separator
    
#     # Write CSV header
#     header = [
#         'Asset ID', 'Description', 'Status', 
#         'Assigned Room', 'Last Located', 
#         'Brand', 'Model', 'Serial Number',
#         'Last Update'
#     ]
#     writer.writerow(header)
    
#     # Write each discrepancy row
#     for asset in discrepancies:
#         writer.writerow([
#             asset.get('id', ''),
#             asset.get('description', ''),
#             asset.get('status', ''),
#             asset.get('room_name', 'Unknown'),
#             asset.get('last_located_name', asset.get('room_name', 'Unknown')),
#             asset.get('brand', ''),
#             asset.get('model', ''),
#             asset.get('serial_number', ''),
#             asset.get('last_update', '') # Format this if needed
#         ])
    
#     # Prepare response
#     output.seek(0)
#     timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
#     filename = f"discrepancy_report_{timestamp}.csv"

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
def get_discrepancies_api():
    try:
        rows = build_discrepancy_rows()
        return jsonify(rows), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to load discrepancies: {str(e)}'
        }), 500


@discrepancy_views.route('/api/bulk-relocations/all', methods=['GET'])
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
    try:
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