from flask import Blueprint, render_template, jsonify, request
from flask_jwt_extended import current_user, jwt_required
from App.controllers.room import *
from App.controllers.audit import *
from App.controllers.checkevent import *
# from App.controllers.asset import (
#     get_all_assets, 
#     get_all_assets_by_room_json, 
#     get_asset, 
#     update_asset_location,
#     mark_assets_missing
# )

audit_views = Blueprint('audit_views', __name__, template_folder='../templates')

@audit_views.route('/audit-list')
@jwt_required()
def audit_list():
    audits = get_all_audits() # Need to get the info from other models 
    return render_template('audit_list.html', audits=audits)

@audit_views.route('/audit-list/<audit_id>', methods=['GET'])
@jwt_required()
def audit_detail(audit_id):
    audit = get_audit_by_id(audit_id) # Need to get the info from other models 

    return render_template('audit_detail.html', audit=audit)

@audit_views.route('/start-audit', methods=['POST'])
@jwt_required()
def start_audit():
    audit = create_audit(current_user.user_id)
    return jsonify(audit.get_json()), 200

@audit_views.route('/end-audit', methods=['POST'])
@jwt_required()
def end_audit_route():
    audit = end_audit()
    if not audit:
        return jsonify({'message': 'No active audit to end'}), 400
    return jsonify(audit.get_json()), 200

@audit_views.route('/compare-audits/<audit_id>/<audit_id2>', methods=['POST'])
@jwt_required()
def compare_audits(audit_id, audit_id2):
    if not get_audit_by_id(audit_id) or not get_audit_by_id(audit_id2):
        return jsonify({'message': 'Audit not found'}), 404
    audit1 = get_audit_by_id(audit_id) # Need to get the info from other models 
    audit2 = get_audit_by_id(audit_id2) # Need to get the info from other models 
    return render_template('compare_audits.html', audits=[audit1, audit2]), 200
    
@audit_views.route('/audit')
@jwt_required()
def audit_page():
    """Render the audit page with building data"""
    buildings = get_all_building_json()
    return render_template('audit.html', buildings=buildings), 200


@audit_views.route('/get-audit-status')
@jwt_required()
def get_audit_status():
    try:
        return jsonify({'status': get_audit_status()}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@audit_views.route('/api/check-event', methods=['POST'])
@jwt_required()
def create_check_event():
    data = request.json
    
    if not data or 'asset_id' not in data or 'room_id' not in data:
        return jsonify({
            'success': False, 
            'message': 'Invalid request data: missing asset_id or room_id field'
        }), 400
    
    asset_id = data['asset_id']
    room_id = data['room_id']
    user_id = current_user.user_id
    found_room_id = data['found_room_id']
    condition_id = data['condition_id'] 
    audit_id = data['audit_id']
    
    # Pass the current user's ID
    check_event = create_check_event(audit_id, asset_id, user_id, found_room_id, condition_id)
    
    if not check_event:
        return jsonify({
            'success': False,
            'message': 'Failed to create check event'
        }), 500

    # Checks if there is a discrepancy in the location
    if check_event_location_discrepancy(check_event):
        create_relocation(check_event.audit_id, check_event.found_room_id, check_event.check_event_id)
        return jsonify({
            'success': True,
            'message': 'Check event created successfully',
            'check_event': check_event.get_json()
        })
        
    # Checks if there is a discrepancy in the condition
    if check_event_condition_discrepancy(check_event):
        # update_asset_assignment(check_event.asset_id, condition=check_event.condition)
        return jsonify({
            'success': True,
            'message': 'Check event created successfully',
            'check_event': check_event.get_json()
        })
    
    return jsonify({
        'success': True,
        'message': 'Check event created successfully',
        'check_event': check_event.get_json()
    })
# @audit_views.route('/api/asset/<asset_id>', methods=['GET'])
# @jwt_required()
# def get_asset_by_id(asset_id):
#     """Get a single asset by ID"""
#     asset = get_asset(asset_id)
    
#     if not asset:
#         return jsonify({'message': 'Asset not found'}), 404
    
#     # Get asset data
#     asset_json = asset.get_json()
    
#     # Add room names
#     if asset.room_id:
#         room = get_room(asset.room_id)
#         if room:
#             asset_json['room_name'] = room.room_name
    
#     if asset.last_located:
#         last_room = get_room(asset.last_located)
#         if last_room:
#             asset_json['last_located_name'] = last_room.room_name
    
#     # Add assignee name - THIS IS THE FIX
#     if asset.assignee_id:
#         assignee = get_assignee_by_id(asset.assignee_id)
#         if assignee:
#             asset_json['assignee_name'] = str(assignee)  # Use __str__
#         else:
#             asset_json['assignee_name'] = f"Assignee ID: {asset.assignee_id}"
#     else:
#         asset_json['assignee_name'] = "Unassigned"
    
#     return jsonify(asset_json)

# @audit_views.route('/api/mark-assets-missing', methods=['POST'])
# @jwt_required()
# def mark_missing():
#     """Mark multiple assets as missing"""
#     data = request.json
    
#     if not data or 'assetIds' not in data:
#         return jsonify({
#             'success': False, 
#             'message': 'Invalid request data: missing assetIds field'
#         }), 400
    
#     asset_ids = data['assetIds']
    
#     if not isinstance(asset_ids, list):
#         return jsonify({
#             'success': False, 
#             'message': 'assetIds must be a list'
#         }), 400
    
#     # Pass the current user's ID
#     processed_count, error_count, errors = mark_assets_missing(asset_ids, current_user.id)
    
#     if processed_count == 0:
#         return jsonify({
#             'success': False,
#             'message': f'Failed to mark assets as missing: {errors[0] if errors else "Unknown error"}',
#             'errors': errors[:10] if errors else [],
#             'processed_count': 0,
#             'error_count': error_count
#         }), 500
    
#     return jsonify({
#         'success': True,
#         'message': f'{processed_count} assets marked as missing',
#         'processed_count': processed_count,
#         'error_count': error_count,
#         'errors': errors[:10] if errors else []
#     })
    
"""
API Routes

"""

@audit_views.route('/api/assets/<room_id>')
@jwt_required()
def get_room_assets(room_id):
    """Get all assets for a given room"""
    try:
        # Get assets for the room
        room_assets = get_all_assets_by_room_json(room_id)
        return jsonify(room_assets)
    except Exception as e:
        return jsonify({"error": str(e)}), 404

@audit_views.route('/api/audit-list')
@jwt_required()
def get_all_audits():
    audits = get_all_audits_json()
    return jsonify(audits), 200

@audit_views.route('/api/audit-list/<audit_id>')
@jwt_required()
def get_audit_by_id(audit_id):
    audit = generate_final_report(audit_id)
    return jsonify(audit), 200

@audit_views.route('/api/generate-iterim-report/<audit_id>')
@jwt_required()
def generate_iterim_report(audit_id):
    audit = generate_iterim_report(audit_id)
    return jsonify(audit), 200

@audit_views.route('/api/compare-audits/<audit_id>/<audit_id2>')
@jwt_required()
def compare_audits_api(audit_id, audit_id2):
    if not get_audit_by_id(audit_id) or not get_audit_by_id(audit_id2):
        return jsonify({'message': 'Audit not found'}), 404
    try:
        audit1 = generate_final_report(audit_id) 
        audit2 = generate_final_report(audit_id2) 
        return jsonify([audit1, audit2]), 200
    except Exception as e:
        return jsonify({'error': 'Could not compare Audits'}), 500

# NEW ENDPOINTS FOR DASHBOARD
from App.models import CheckEvent, MissingDevice, Relocation, db

@audit_views.route('/api/audit/<audit_id>/checkevents', methods=['GET'])
@jwt_required()
def api_audit_checkevents(audit_id):
    query = CheckEvent.query.filter_by(audit_id=audit_id)
    status_filter = request.args.get('status')
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    events = query.all()
    return jsonify([e.get_json() for e in events]), 200

@audit_views.route('/api/audit/<audit_id>/missing', methods=['GET'])
@jwt_required()
def api_audit_missing(audit_id):
    missing_items = MissingDevice.query.filter_by(audit_id=audit_id).all()
    return jsonify([{
        'missing_id': m.missing_id,
        'assignment_id': m.assignment_id,
        'date': m.date.strftime('%Y-%m-%d %H:%M:%S'),
        'found_relocation_id': m.found_relocation_id
    } for m in missing_items]), 200

@audit_views.route('/api/checkevent/<check_id>/resolve', methods=['POST'])
@jwt_required()
def api_resolve_relocation(check_id):
    # This route will change a pending relocation to relocated
    event = CheckEvent.query.get(check_id)
    if not event:
        return jsonify({'message': 'Check event not found'}), 404
        
    if event.status != 'pending relocation':
        return jsonify({'message': 'Event is not pending relocation'}), 400
        
    event.status = 'relocated'
    
    # We should also register the explicit Relocation if missing
    # To keep it simple, we just update CheckEvent state here to unblock audit closing
    db.session.commit()
    
    return jsonify({'message': 'Relocation resolved', 'event': event.get_json()}), 200