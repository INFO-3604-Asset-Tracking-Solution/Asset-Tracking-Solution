from datetime import datetime
from App.models import Asset, AssetStatus
from sqlalchemy.exc import IntegrityError
from App.database import db
import csv
from App.models import Employee
from App.controllers.employee import create_employee, get_employee_by_email



def get_asset(asset_id):
    return Asset.query.filter_by(asset_id=asset_id).first()

def get_all_assets():
    return Asset.query.all()

def get_all_assets_json():
    assets = get_all_assets()
    if not assets:
        return[]
    assets = [asset.get_json() for asset in assets]
    return assets

def add_asset(description, brand, model, serial_number, cost, notes, status_name="Available"): 
    try:
        status = AssetStatus.query.filter_by(status_name = status_name).first()

        if not status:
            print(f"Invalid status: {status_name}")
        
        newAsset = Asset(
            description = description, 
            brand = brand, 
            model = model, 
            serial_number = serial_number, 
            cost = cost, 
            notes = notes, 
            status_id = status.status_id, 
            last_update = datetime.utcnow()
        )

        db.session.add(newAsset)
        db.session.commit()
        return newAsset

    except ValueError:
        db.session.rollback()
        print(f"Error: Invalid asset status '{asset_status}'.")
        return None

    except IntegrityError: # Catch specific duplicate key error
        db.session.rollback()
        print(f"Error: Asset with ID {asset_id} already exists.")
        return None

    except Exception as e: # Catch other potential errors
        db.session.rollback()
        print(f"Error adding asset {asset_id}: {e}")
        return None

def upload_csv(file_path):
    from App.controllers.room import get_room_by_name
    from App.controllers.assetassignment import create_asset_assignment

    results = {
        'success': False,
        'total': 0,
        'imported': 0,
        'skipped': 0,
        'errors': []
    }

    try:
        # 1. Ensure/Get the Placeholder Employee
        placeholder_email = "bulk.import@auto.generated"
        placeholder = get_employee_by_email(placeholder_email)
        if not placeholder:
            placeholder = create_employee("Bulk Import", "Placeholder", placeholder_email)
            if not placeholder:
                results['errors'].append("Critical Error: Could not create placeholder employee for assignments.")
                return results

        # 2. Process the CSV
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)

            # Match the 6 columns approved in the plan
            expected_columns = ["Item", "Brand", "Model", "Serial Number", "Cost", "Location"]
            actual_columns = [col.strip() for col in reader.fieldnames]

            missing_columns = [col for col in expected_columns if col not in actual_columns]
            if missing_columns:
                results['errors'].append(f"Missing required columns: {', '.join(missing_columns)}")
                return results

            for row_num, row in enumerate(reader, start=2):
                results['total'] += 1
                
                try:
                    item_name = (row.get("Item") or "").strip()
                    location_name = (row.get("Location") or "").strip()
                    
                    if not item_name:
                        results['errors'].append(f"Row {row_num}: Missing 'Item' description.")
                        results['skipped'] += 1
                        continue

                    # Lookup Room
                    if not location_name:
                        results['errors'].append(f"Row {row_num}: Missing 'Location' (Room Name).")
                        results['skipped'] += 1
                        continue
                        
                    room = get_room_by_name(location_name)
                    if not room:
                        results['errors'].append(f"Row {row_num}: Room '{location_name}' not found.")
                        results['skipped'] += 1
                        continue

                    # Add the Asset
                    # Note: Using positional arguments as per current add_asset signature
                    # description, brand, model, serial_number, cost, notes, status_name="Available"
                    cost_val = None
                    try:
                        if row.get("Cost"):
                            cost_val = float(str(row["Cost"]).replace('$', '').replace(',', ''))
                    except:
                        pass

                    new_asset = add_asset(
                        item_name,
                        (row.get("Brand") or "").strip(),
                        (row.get("Model") or "").strip(),
                        (row.get("Serial Number") or "").strip(),
                        cost_val,
                        "Bulk Imported Asset",
                        "Available"
                    )

                    if new_asset:
                        # Create Assignment
                        assignment = create_asset_assignment(
                            new_asset.asset_id,
                            placeholder.employee_id,
                            room.room_id,
                            "Good"
                        )
                        if assignment:
                            results['imported'] += 1
                        else:
                            results['errors'].append(f"Row {row_num}: Asset created but failed to link to Location.")
                            results['imported'] += 1 # Still technically imported
                    else:
                        results['errors'].append(f"Row {row_num}: Database error while creating asset.")
                        results['skipped'] += 1

                except Exception as e:
                    db.session.rollback()
                    results['errors'].append(f"Row {row_num}: Unexpected error - {str(e)}")
                    results['skipped'] += 1

            # Set success if at least one asset was imported
            results['success'] = results['imported'] > 0
            return results

    except Exception as e:
        results['errors'].append(f"File processing error: {str(e)}")
        return results


def delete_asset(asset_id):
    asset = get_asset(asset_id)

    if not asset:
        return False, f"Asset {asset_id} does not exist."

    try:
        db.session.delete(asset)
        db.session.commit()
        return True, f"Asset {asset_id} was successfully deleted."
        
    except Exception as e: # Catch specific exceptions if needed
            db.session.rollback()
            return False, f"Failed to delete asset {asset_id}. Error: {str(e)}"
    

def update_asset_details(asset_id, description, model, brand, serial_number, cost, notes, asset_status=None):
    asset = get_asset(asset_id)
    if not asset:
        return None

    # Update only the editable fields
    asset.description = description
    asset.model = model
    asset.brand = brand
    asset.serial_number = serial_number
    asset.cost = cost
    asset.notes = notes
    asset.last_update = datetime.utcnow() # Automatically update the last_update timestamp

    if asset_status:
        status = AssetStatus.query.filter_by(status_name = asset_status).first()

        if status:
            asset.status_id = status.status_id
        else:
            print(f"Invalid status '{asset_status}' provided")


    try:

        db.session.commit()
        return asset

    except Exception as e:
        print(f"Error updating asset details for {asset_id}: {e}")
        db.session.rollback()
        return None

