from App.models import Room
from App.database import db

def create_room(room_id, floor_id, building_id, room_name):

    existing_room = Room.query.filter_by(room_id = room_id).first()
    if existing_room:
        return None
    
    new_room = Room(
        room_id=room_id, 
        floor_id=floor_id, 
        building_id = building_id,
        room_name=room_name
    )

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

def get_rooms_by_building(building_id):
    return Room.query.filter_by(building_id = building_id).all()

def get_all_rooms():
    return Room.query.all()

def get_all_rooms_json():
    rooms = get_all_rooms()

    if not rooms: 
        return []
    
    return [room.get_json() for room in rooms]

def update_room(room_id, floor_id = None, building_id = None, room_name = None):
    room = get_room(room_id)
    
    if not room: 
        return None

    if floor_id:
        room.floor_id = floor_id
    
    if building_id:
        room.building_id = building_id

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
        return False  # Room not found

    try:
        db.session.delete(room)
        db.session.commit()
        return True
    
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting room: {e}")
        return False
