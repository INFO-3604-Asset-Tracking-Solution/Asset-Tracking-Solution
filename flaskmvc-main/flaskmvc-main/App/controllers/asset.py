from datetime import datetime
from App.models import Asset, AssetStatus
from sqlalchemy.exc import IntegrityError # Import IntegrityError
from App.database import db
import csv


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

def add_asset(asset_id, condition_id, description, brand, model, serial_number, cost, notes, asset_status="Available"): 
    try:
        status = AssetStatus.query.filter_by(status_name = asset_status).first()

        if not status:
            print(f"Invalid status: {asset_status}")
        
        newAsset = Asset(
            asset_id = asset_id, 
            condition_id = condition_id, 
            status_id = status.status_id, 
            description = description, 
            brand = brand, 
            model = model, 
            serial_number = serial_number, 
            cost = cost, 
            notes = notes, 
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
    results = {
        'success': False,
        'total': 0,
        'imported': 0,
        'skipped': 0,
        'errors': []
    }

    try:
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)

            expected_columns = [
                "Item", 
                "Asset Tag", 
                "Model", 
                "Brand", 
                "Serial Number",
                "Cost", 
                "Status"
            ]
            actual_columns = [col.strip() for col in reader.fieldnames]

            missing_columns = [col for col in expected_columns if col not in actual_columns]
            if missing_columns:
                results['errors'].append(f"Missing required columns: {', '.join(missing_columns)}")
                return results

            for row_num, row in enumerate(reader, start=2):  # Start at 2 to account for header row
                results['total'] += 1

                try:
                    status_str = row.get("Status", "Available")

                    new_asset = add_asset(
                        asset_id= row["Asset Tag"],
                        condition_id = 1,
                        asset_status = status_str,
                        description= row["Item"],
                        model=row["Model"],
                        brand=row["Brand"],
                        serial_number=row["Serial Number"],
                        cost = float(row["Cost"]) if row["Cost"] else None,
                        notes= None
                    )

                    if new_asset:
                        results['imported'] += 1
                    else:
                        results['skipped'] += 1

                except IntegrityError as e:
                    db.session.rollback()
                    # Check if it's specifically a duplicate primary key error
                    # This check depends slightly on the DB engine, but often contains 'UNIQUE constraint' or 'Duplicate entry'
                    error_str = str(e).lower() # Convert error to lowercase string for easier checking
                    if 'unique constraint' in error_str \
                    or 'duplicate entry' in error_str \
                    or 'violates unique constraint' in error_str \
                    or (hasattr(e, 'orig') and 'duplicate key value violates unique constraint' in str(e.orig).lower()): # More specific check for psycopg2
                        results['errors'].append(f"Row {row_num}: Asset Tag '{row.get('Asset Tag', '')}' already exists, skipped.")
                    else:
                        # Other type of IntegrityError (e.g., foreign key violation if a room didn't exist and wasn't handled)
                        results['errors'].append(f"Row {row_num}: Database integrity error - {str(e)}")
                    results['skipped'] += 1
                except Exception as e:
                    db.session.rollback()
                    results['errors'].append(f"Row {row_num}: Error processing row - {str(e)}")
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

