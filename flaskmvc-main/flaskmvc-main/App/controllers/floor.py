from App.models import Floor, Building
from App.database import db

def create_floor(building_id, floor_name):
    # Ensure building exists
    building = Building.query.get(building_id)
    if not building:
        return None
    
    existing_floor = Floor.query.filter_by(building_id=building_id, floor_name=floor_name).first()
    if existing_floor:
        return existing_floor
    
    new_floor = Floor(building_id=building_id, floor_name=floor_name)
    try:
        db.session.add(new_floor)
        db.session.commit()
        return new_floor
    except Exception as e:
        db.session.rollback()
        print(f"Error creating floor: {e}")
        return None

def get_floor(floor_id):
    return Floor.query.get(floor_id)

def get_all_floors():
    return Floor.query.all()

def get_all_floors_json():
    floors = get_all_floors()
    return [floor.get_json() for floor in floors]

def get_floors_by_building(building_id):
    return Floor.query.filter_by(building_id=building_id).all()

def update_floor(floor_id, building_id=None, floor_name=None):
    floor = get_floor(floor_id)
    if not floor:
        return None
    
    if building_id:
        # Ensure new building exists
        building = Building.query.get(building_id)
        if building:
            floor.building_id = building_id
            
    if floor_name:
        floor.floor_name = floor_name
        
    try:
        db.session.commit()
        return floor
    except Exception as e:
        db.session.rollback()
        print(f"Error updating floor: {e}")
        return None

def delete_floor(floor_id):
    floor = get_floor(floor_id)
    if not floor:
        return False
    try:
        db.session.delete(floor)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting floor: {e}")
        return False
