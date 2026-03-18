from datetime import datetime
from App.models import Relocation, CheckEvent, Room
from App.database import db

def create_relocation(check_id, found_room_id, new_check_event_id):
    check = CheckEvent.query.get(check_id)
    room = Room.query.get(found_room_id)

    if new_check_event_id is not None:
        new_check = CheckEvent.query.get(new_check_event_id)
        if not new_check:
            return None
            
    if not check or not room:
        return None


    relocation =  Relocation(
        check_id = check_id,
        found_room_id = found_room_id,
        new_check_event_id = new_check_event_id,
        timestamp = datetime.utcnow()
    )

    db.session.add(relocation)
    db.session.commit()

    return relocation

def get_all_relocations():
    return Relocation.query.all()

def get_relocation(relocation_id):
    return Relocation.query.get(relocation_id)

def get_relocation_by_check(check_id):
    return Relocation.query.filter_by(check_id = check_id).all()
