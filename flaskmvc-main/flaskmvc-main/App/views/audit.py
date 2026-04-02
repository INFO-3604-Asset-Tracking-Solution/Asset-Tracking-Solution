from flask import Blueprint, render_template, jsonify, request 
from flask_jwt_extended import current_user, jwt_required
from App.controllers.building import get_all_building_json
from App.controllers.floor import get_floors_by_building
from App.controllers.room import get_rooms_by_floor, get_room
from App.controllers.asset import (
    get_all_assets, 
    get_all_assets_by_room_json, 
    get_asset, 
    update_asset_location,
    mark_assets_missing
)
from App.controllers.assignee import get_assignee_by_id
from App.decorators import role_required  # Added for role-based access

audit_views = Blueprint('audit_views', __name__, template_folder='../templates')

@audit_views.route('/audit-list')
@jwt_required()
@role_required(['Administrator', 'Manager', 'Auditor/Scanner'])  # Role access
def audit_page():
    """Render the audit page with building data"""
    buildings = get_all_building_json()
    return render_template('audit.html', buildings=buildings)

@audit_views.route('/audit-list/<audit_id>', methods=['GET'])
@jwt_required()
@role_required(['Administrator', 'Manager', 'Auditor/Scanner'])
def get_floors(building_id):
    """Get all floors for a given building"""
    floors = get_floors_by_building(building_id)
    
    # Handle case with no floors
    if not floors:
        return jsonify([])
        
    floors_json = [floor.get_json() for floor in floors]
    return jsonify(floors_json)

@audit_views.route('/start-audit', methods=['GET'])
@jwt_required()
@role_required(['Administrator', 'Manager', 'Auditor/Scanner'])
def get_rooms(floor_id):
    """Get all rooms for a given floor"""
    rooms = get_rooms_by_floor(floor_id)
    
    return render_template('audit_list.html', audits=audits), 200

@audit_views.route('/end-audit', methods=['GET'])
@jwt_required()
@role_required(['Administrator', 'Manager', 'Auditor/Scanner'])
def get_room_assets(room_id):
    """Get all assets for a given room"""
    try:
        # Get assets for the room
        room_assets = get_all_assets_by_room_json(room_id)
        
        # Enhance the assets with room name and assignee information
        for asset in room_assets:
            # Add room names where possible
            if 'room_id' in asset:
                room = get_room(asset['room_id'])
                if room:
                    asset['room_name'] = room.room_name
            
            if 'last_located' in asset:
                last_room = get_room(asset['last_located'])
                if last_room:
                    asset['last_located_name'] = last_room.room_name
            
            # Add assignee name information - THIS IS THE FIX
            if asset.get('assignee_id'):
                assignee = get_assignee_by_id(asset['assignee_id'])
                if assignee:
                    asset['assignee_name'] = str(assignee)  # Use __str__
                else:
                    asset['assignee_name'] = f"Assignee ID: {asset['assignee_id']}"
            else:
                asset['assignee_name'] = "Unassigned"
        
        return jsonify(room_assets)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@audit_views.route('/compare-audits/<audit_id>/<audit_id2>', methods=['POST'])
@jwt_required()
@role_required(['Administrator', 'Manager', 'Auditor/Scanner'])
def get_asset_by_id(asset_id):
    """Get a single asset by ID"""
    asset = get_asset(asset_id)
    
    if not asset:
        return jsonify({'message': 'Asset not found'}), 404
    
    # Get asset data
    asset_json = asset.get_json()
    
    # Add room names
    if asset.room_id:
        room = get_room(asset.room_id)
        if room:
            asset_json['room_name'] = room.room_name
    
    if asset.last_located:
        last_room = get_room(asset.last_located)
        if last_room:
            asset_json['last_located_name'] = last_room.room_name
    
    # Add assignee name - THIS IS THE FIX
    if asset.assignee_id:
        assignee = get_assignee_by_id(asset.assignee_id)
        if assignee:
            asset_json['assignee_name'] = str(assignee)  # Use __str__
        else:
            asset_json['assignee_name'] = f"Assignee ID: {asset.assignee_id}"
    else:
        asset_json['assignee_name'] = "Unassigned"
    
@audit_views.route('/audit')
@jwt_required()
def audit_page():
    """Render the audit page with building data"""
    buildings = get_all_buildings_json()
    return render_template('audit.html', buildings=buildings), 200


@audit_views.route('/get-audit-status')
@jwt_required()
@role_required(['Administrator', 'Manager', 'Auditor/Scanner'])
def mark_missing():
    """Mark multiple assets as missing"""
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
    
@audit_views.route('/api/update-asset-location', methods=['POST'])
@jwt_required()
@role_required(['Administrator', 'Manager', 'Auditor/Scanner'])
def update_location():
    """Update an asset's location"""
    data = request.json
    
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

@audit_views.route('/api/start-audit', methods=['POST'])
@jwt_required()
def start_audit_api():
    audit = create_audit(current_user.user_id)
    return jsonify(audit.get_json()), 200

@audit_views.route('/api/assets/<room_id>', methods=['GET'])
@jwt_required()
def get_room_assets(room_id):
    """Get all assets for a given room"""
    try:
        # Get assets for the room
        room_assets = get_asset_list_from_assignments_for_room_json(room_id)
        return jsonify(room_assets)
    except Exception as e:
        return jsonify({"error": str(e)}), 404

@audit_views.route('/api/audit-list')
@jwt_required()
def get_all_audits_api():
    audits = get_all_audits_json()
    return jsonify(audits), 200

@audit_views.route('/api/audit-list/<audit_id>')
@jwt_required()
def get_audit_by_id_api(audit_id):
    audit = generate_final_report(audit_id)
    return jsonify(audit), 200

@audit_views.route('/api/generate-iterim-report/<audit_id>')
@jwt_required()
def generate_iterim_report_api(audit_id):
    audit = generate_interim_report(audit_id)
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

