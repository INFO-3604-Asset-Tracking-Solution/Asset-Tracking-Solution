from datetime import datetime
from App.models import Relocation, AssetAssignment, Room
from App.database import db

def create_relocation(assignment_id, found_room_id):

    assignment = AssetAssignment.query.get(assignment_id)
    room = Room.query.get(found_room_id)

    if not assignment or not room:
        return None

    if assignment.room_id == found_room_id:
        return None

    relocation =  Relocation(
        assignment_id = assignment_id,
        found_room_id = found_room_id,
        date = datetime.utcnow(),
        status = "RELOCATED"
    )

    db.session.add(relocation)
    db.session.commit()

    return relocation

def get_all_relocations():
    return Relocation.query.all()

def get_relocation(relocation_id):
    return Relocation.query.get(relocation_id)

def get_relocation_by_assignment(assignment_id):
    return Relocation.query.filter_by(assignment_id = assignment_id).all()

def get_relocations_by_asset(asset_id):
    return Relocation.query.join(AssetAssignment).filter(AssetAssignment.asset_id == asset_id).all()