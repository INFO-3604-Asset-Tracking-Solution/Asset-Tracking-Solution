from App.models import AssetAssignment, Asset, Room, Employee
from App.database import db
from datetime import datetime

def create_asset_assignment(asset_id, employee_id, room_id, condition):
    asset = Asset.query.get(asset_id)
    employee = Employee.query.get(employee_id)
    room = Room.query.get(room_id)

    if not asset or not employee or not room:
        return None

    assignment = AssetAssignment(
        asset_id=asset_id,
        employee_id=employee_id,    
        room_id = room_id,
        condition = condition
    )
    db.session.add(assignment)
    db.session.commit()

    return assignment

def end_assignment(assignment_id):

    assignment = AssetAssignment.query.get(assignment_id)

    if not assignment:
        return None

    assignment.end_date = datetime.utcnow()

    db.session.commit()

    return assignment

def get_all_asset_assignment():
    return AssetAssignment.query.all()

def get_all_asset_assignment_json():
    assignments = get_all_asset_assignment()

    if not assignments:
        return[]

    return [assignment.get_json() for assignment in assignments]

def get_asset_assignment_by_id(assignment_id):
    return AssetAssignment.query.get(assignment_id)

def get_current_asset_assignment(asset_id):
    return AssetAssignment.query.filter_by(asset_id = asset_id, end_date = None).first()

def get_assignments_by_employee(employee_id):
    return AssetAssignment.query.filter_by(employee_id = employee_id).all()

def get_assignments_by_asset(asset_id):
    return AssetAssignment.query.filter_by(asset_id = asset_id).all()

def update_asset_assignment(assignment_id, asset_id=None, employee_id=None, start_date=None, end_date=None, condition=None):
    assignment = get_asset_assignment_by_id(assignment_id)
    if assignment:
        if asset_id:
            assignment.asset_id = asset_id
        if employee_id:
            assignment.employee_id = employee_id
        if start_date:
            assignment.start_date = start_date
        if end_date is not None:
            assignment.end_date = end_date
        if condition:
            assignment.condition = condition
        
        db.session.commit()
        return assignment

    return None

def delete_asset_assignment(assignment_id):
    assignment = get_asset_assignment_by_id(assignment_id)
    if assignment:
        db.session.delete(assignment)
        db.session.commit()
        return True
    
    return False

