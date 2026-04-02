from App.models import AssetAssignment, Asset, Room, Employee
from App.database import db
from datetime import datetime

def create_asset_assignment(asset_id, employee_id, room_id, condition, assign_date=None, return_date=None):

    asset = Asset.query.filter_by(asset_id=asset_id).first()
    employee = Employee.query.filter_by(employee_number=str(employee_id)).first()
    room = Room.query.filter_by(room_code=str(room_id).upper()).first()

    if not asset or not employee or not room:
        return None

    if assign_date:
        assign_date = datetime.fromisoformat(assign_date)
    else:
        assign_date = datetime.utcnow()

    if return_date:
        return_date = datetime.fromisoformat(return_date)

    assignment = AssetAssignment(
        asset_id=asset_id,
        employee_id=employee.employee_id,
        room_id=room.room_id,
        condition=condition,
        assignment_date=assign_date,
        return_date=return_date
    )

    db.session.add(assignment)
    db.session.commit()

    return assignment

def end_assignment(assignment_id):

    assignment = AssetAssignment.query.get(assignment_id)

    if not assignment:
        return None

    assignment.return_date = datetime.utcnow()

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
    return AssetAssignment.query.filter_by(asset_id = asset_id, return_date = None).first()

def get_assignments_by_employee(employee_number):
    employee = Employee.query.filter_by(employee_number=employee_number).first()
    if not employee:
        return []
    return AssetAssignment.query.filter_by(employee_id = employee.employee_id).all()

def get_assignments_by_room(room_code):
    room = Room.query.filter_by(room_code=room_code.upper()).first()
    if not room:
        return []
    return AssetAssignment.query.filter_by(room_id = room.room_id).all()


def get_assignments_by_asset(asset_id):
    return AssetAssignment.query.filter_by(asset_id = asset_id).all()

def update_asset_assignment(assignment_id, asset_id=None, employee_id=None, room_id=None, return_date=None, condition=None, status=None):
    assignment = get_asset_assignment_by_id(assignment_id)
    if assignment:
        if asset_id:
            assignment.asset_id = asset_id
        if employee_id:
            employee = Employee.query.filter_by(employee_number=str(employee_id)).first()
            if employee:
                assignment.employee_id = employee.employee_id
        if room_id:
            room = Room.query.filter_by(room_code=str(room_id).upper()).first()
            if room:
                assignment.room_id = room.room_id
        if return_date is not None:
            assignment.return_date = datetime.fromisoformat(return_date) if return_date else None
        if condition:
            assignment.condition = condition
        if status:
            assignment.status = status

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

