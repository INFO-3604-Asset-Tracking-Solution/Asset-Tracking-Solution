from App.models import AssetStatus
from App.database import db

def create_asset_status(status_name):
    existing_status = AssetStatus.query.filter_by(status_name=status_name).first()
    if existing_status:
        print(f"Warning: Asset status {status_name} already exists. Cannot create duplicate.")
        return None

    new_asset_status = AssetStatus(status_name)

    try:
        db.session.add(new_asset_status)
        db.session.commit()
        return new_asset_status
    except Exception as e:
        db.session.rollback()
        print(f"Error creating asset status: {e}")
        return None


def get_asset_status_by_id(status_id):
    try:
        return AssetStatus.query.get(int(status_id))
    except (ValueError, TypeError):
        return None


def get_asset_status_by_name(status_name):
    return AssetStatus.query.filter_by(status_name=status_name).first()


def get_all_asset_statuses():
    return AssetStatus.query.all()


def get_all_asset_statuses_json():
    asset_statuses = AssetStatus.query.all()
    if not asset_statuses:
        return []

    asset_statuses = [asset_status.get_json() for asset_status in asset_statuses]
    return asset_statuses


def update_asset_status(status_id, status_name):
    asset_status = get_asset_status_by_id(status_id)

    if asset_status:
        asset_status.status_name = status_name
        

        try:
            db.session.commit()
            return asset_status
        except Exception as e:
            db.session.rollback()
            print(f"Error updating asset status: {e}")
            return None

    return None


def delete_asset_status(status_id):
    asset_status = get_asset_status_by_id(status_id)

    if asset_status:
        try:
            db.session.delete(asset_status)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting asset status: {e}")
            return False

    return False