from App.models import Building
from App.database import db

def create_building(building_name):
    existing_building = Building.query.filter_by(building_name=building_name).first()
    if existing_building:
        return existing_building
    
    new_building = Building(building_name=building_name)
    try:
        db.session.add(new_building)
        db.session.commit()
        return new_building
    except Exception as e:
        db.session.rollback()
        print(f"Error creating building: {e}")
        return None

def get_building(building_id):
    return Building.query.get(building_id)

def get_building_by_name(building_name):
    return Building.query.filter_by(building_name=building_name).first()

def get_all_buildings():
    return Building.query.all()

def get_all_buildings_json():
    buildings = get_all_buildings()
    return [building.get_json() for building in buildings]

def update_building(building_id, building_name=None):
    building = get_building(building_id)
    if not building:
        return None
    if building_name:
        building.building_name = building_name
    try:
        db.session.commit()
        return building
    except Exception as e:
        db.session.rollback()
        print(f"Error updating building: {e}")
        return None

def delete_building(building_id):
    building = get_building(building_id)
    if not building:
        return False
    try:
        db.session.delete(building)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting building: {e}")
        return False
