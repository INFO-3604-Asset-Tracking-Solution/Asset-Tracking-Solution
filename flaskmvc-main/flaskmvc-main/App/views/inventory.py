from flask import Blueprint, render_template, jsonify, request
from flask_jwt_extended import jwt_required, current_user
from App.controllers.asset import *
from App.controllers.room import *
from App.controllers.assetassignment import *
from App.controllers.employee import *
from App.models.assetassignment import AssetAssignment
from App.models.assetstatus import AssetStatus
from App.controllers.room import get_all_rooms_json
from datetime import datetime
from functools import wraps
from App.database import db

inventory_views = Blueprint('inventory_views', __name__, template_folder='../templates')

def require_roles(*roles):
    def wrapper(fn):
        @wraps(fn)
        def decorated(*args, **kwargs):
            user = current_user

            role = getattr(user, "role", None)

            if role not in roles:
                return jsonify({"message": "Access denied"}), 403

            return fn(*args, **kwargs)
        return decorated
    return wrapper

@inventory_views.route('/inventory', methods=['GET'])
@jwt_required()
def inventory_page():
    return render_template('inventory.html')

from App.models.assetassignment import AssetAssignment  


# ----------ASSETS-----------

@inventory_views.route('/api/assets', methods=['GET'])
@jwt_required()
def get_assets():
    from App.controllers.assetassignment import get_current_asset_assignment
    
    assets = get_all_assets_json()

    for asset in assets:
        # Get status name
        if asset.get('status_id'):
            status = AssetStatus.query.get(asset['status_id'])
            asset['status_name'] = status.status_name if status else "Unknown"

        # Try to find current assignment to get the room
        assignment = get_current_asset_assignment(asset['asset_id'])
        if assignment:
            room = get_room(assignment.room_id)
            asset['room_id'] = assignment.room_id
            asset['room_name'] = room.room_name if room else "Unknown"
            
            # Also fetch assignee if possible
            employee = assignment.employee
            if employee:
                asset['assignee_name'] = f"{employee.first_name} {employee.last_name}"
            else:
                asset['assignee_name'] = "Unassigned"
        else:
            asset['room_id'] = None
            asset['room_name'] = "N/A"
            asset['assignee_name'] = "Unassigned"

    return jsonify(assets)

@inventory_views.route('/api/asset/add', methods=['POST'])
@jwt_required()
@require_roles("Administrator", "Manager")
def add_asset_api():

    data = request.json

    if not data:
        return jsonify({'success': False, 'message': 'No data'}), 400

    try:
        description = data.get('description')

        if not description:
            return jsonify({'success': False, 'message': 'Missing required field'}), 400

        new_asset = add_asset(
            description=description,
            brand=data.get('brand'),
            model=data.get('model'),
            serial_number=data.get('serial_number'),
            cost =float(data.get('cost')) if data.get('cost') else None,
            notes=data.get('notes'),
            status_name=data.get('status_name', 'Available')
        )

        if not new_asset:
            return jsonify({'success': False, 'message': 'Failed to create asset'}), 400

        return jsonify({
            'success': True,
            'asset': new_asset.get_json()
        }), 201
            
    except Exception as e:
        print("Add asset error:", e)
        return jsonify({'success': False, 'message': 'Server error'}), 500


@inventory_views.route('/asset/<asset_id>', methods=['GET'])
@jwt_required()
def asset_page(asset_id):
    asset = get_asset(asset_id)

    if not asset:
        return "Asset not found", 404

    return render_template('asset_edit.html', asset=asset)


@inventory_views.route('/api/asset/<asset_id>/update', methods=['POST'])
@jwt_required()
@require_roles("Administrator", "Manager")
def update_asset_details_endpoint(asset_id):

    data = request.json

    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400

    updated_asset = update_asset_details(
        asset_id,
        data.get('description'),
        data.get('model'),
        data.get('brand'),
        data.get('serial_number'),
        None,
        data.get('notes')
    )

    if not updated_asset:
        return jsonify({'success': False, 'message': 'Update failed'}), 404

    return jsonify({
        'success': True,
        'asset': updated_asset.get_json()
    })
    
@inventory_views.route('/api/asset/<asset_id>/delete', methods=['POST'])
@jwt_required()
@require_roles("Administrator", "Manager")
def delete_asset_route(asset_id):

    try:
        from App.controllers.asset import delete_asset
        success, message = delete_asset(asset_id)

        if not success:
            return jsonify({'success': False, 'message': message}), 404

        return jsonify({'success': True, 'message': message})

    except Exception as e:
        print("Delete asset error:", e)
        return jsonify({'success': False, 'message': 'Server error'}), 500


# ----------ROOMS-----------

@inventory_views.route('/api/rooms/all', methods=['GET'])
@jwt_required()
def get_rooms():
    return get_all_rooms_json() 


# ----------EMPLOYEES-----------

@inventory_views.route('/api/employees/all', methods=['GET'])
@jwt_required()
def get_employees():
    return get_all_employees_json()


# ----------ASSET ASSIGNMENTS-----------

@inventory_views.route('/api/assignments', methods=['GET'])
@jwt_required()
def get_assignments():
    return jsonify(get_all_asset_assignment_json())


@inventory_views.route('/api/assignments', methods=['POST'])
@jwt_required()
@require_roles("Administrator", "Manager")
def create_assignment_route():

    data = request.json
    print(data)
    if not data:
        return jsonify({'success': False, 'message': 'No data'}), 400

    try:
        asset_id = data.get('asset_id')
        employee_id = data.get('employee_id')
        room_id = data.get('room_id')

        assignment = create_asset_assignment(
            asset_id=asset_id,
            employee_id=employee_id,
            room_id=room_id,
            condition=data.get('condition'),
            assign_date=data.get('assign_date'),
            #return_date=data.get('return_date') or None,
            #status="Active"
        )

        if not assignment:
            return jsonify({'success': False, 'message': 'Failed to create assignment'}), 400

        return jsonify({'success': True, 'assignment': assignment.get_json()}), 201

    except Exception as e:
        print("Create assignment error:", e)
        return jsonify({'success': False, 'message': str(e)}), 500


@inventory_views.route('/api/assignments/<assignment_id>/end', methods=['POST'])
@jwt_required()
def end_assignment_route(assignment_id):
    try:
        updated = end_assignment(assignment_id)

        if not updated:
            return jsonify({'success': False, 'message': 'Not found'}), 404

        return jsonify({
            'success': True,
            'assignment': updated.get_json()
        })

    except Exception as e:
        print("End assignment error:", e)
        return jsonify({'success': False, 'message': 'Server error'}), 500

@inventory_views.route('/assignment/<assignment_id>', methods=['GET'])
@jwt_required()
@require_roles("Administrator", "Manager", "Auditor")
def assignment_edit_page(assignment_id):

    from App.controllers.assetassignment import get_asset_assignment_by_id
    assignment = get_asset_assignment_by_id(assignment_id)

    if not assignment:
        return "Assignment not found", 404

    return render_template('assignment_edit.html', assignment=assignment)

@inventory_views.route('/api/assignments/<assignment_id>/update', methods=['POST'])
@jwt_required()
def update_assignment(assignment_id):

    data = request.get_json()

    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400

    assignment = AssetAssignment.query.get(assignment_id)
    if not assignment:
        return jsonify({"success": False, "message": "Assignment not found"}), 404

    role = current_user.role

    try:

        # AUDITOR PERMISSIONS ONLY
        if role == "Auditor":

            if "return_date" in data:
                assignment.return_date = (
                    datetime.strptime(data["return_date"], "%Y-%m-%d")
                    if data["return_date"] else None
                )

            if "condition" in data and data["condition"]:
                assignment.condition = data["condition"]

        # ADMIN / MANAGER PERMISSIONS
        else:

            if "asset_id" in data and data["asset_id"]:
                assignment.asset_id = data["asset_id"]

            if "employee_id" in data and data["employee_id"]:
                assignment.employee_id = data["employee_id"]

            if "room_id" in data and data["room_id"]:
                assignment.room_id = data["room_id"]

            if "condition" in data and data["condition"]:
                assignment.condition = data["condition"]

            if "return_date" in data:
                assignment.return_date = (
                    datetime.strptime(data["return_date"], "%Y-%m-%d")
                    if data["return_date"] else None
                )

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Assignment updated successfully",
            "assignment": assignment.get_json() if hasattr(assignment, "get_json") else None
        }), 200

    except Exception as e:
        db.session.rollback()
        print("UPDATE ERROR:", e)

        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}"
        }), 500


@inventory_views.route('/api/assignments/<assignment_id>/delete', methods=['POST'])
@jwt_required()
@require_roles("Administrator", "Manager")
def delete_assignment_route(assignment_id):

    try:
        from App.controllers.assetassignment import delete_asset_assignment
        success = delete_asset_assignment(assignment_id)

        if not success:
            return jsonify({'success': False, 'message': 'Not found'}), 404

        return jsonify({'success': True})

    except Exception as e:
        print("Delete assignment error:", e)
        return jsonify({'success': False, 'message': 'Server error'}), 500

