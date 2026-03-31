from App.models import Room
from App.database import db

def create_room(floor_id, room_name):
    existing_room = Room.query.filter_by(floor_id=floor_id, room_name=room_name).first()
    if existing_room:
        return existing_room
    
    new_room = Room(floor_id=floor_id, room_name=room_name)
    try:
        db.session.add(new_room)
        db.session.commit()
        return new_room
    except Exception as e:
        db.session.rollback()
        print(f"Error creating room: {e}")
        return None

def get_room(room_id):
    return Room.query.get(room_id)

def get_rooms_by_floor(floor_id):
    return Room.query.filter_by(floor_id=floor_id).all()

def get_all_rooms():
    return Room.query.all()

def get_all_rooms_json():
    rooms = get_all_rooms()
    return [room.get_json() for room in rooms]

def update_room(room_id, floor_id=None, room_name=None):
    room = get_room(room_id)
    if not room: 
        return None
    if floor_id:
        room.floor_id = floor_id
    if room_name:
        room.room_name = room_name
    try:
        db.session.commit()
        return room
    except Exception as e:
        db.session.rollback()
        print(f"Error updating room: {e}")
        return None

def delete_room(room_id):
    room = get_room(room_id)
    if not room:
        return False
    try:
        db.session.delete(room)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting room: {e}")
        return False