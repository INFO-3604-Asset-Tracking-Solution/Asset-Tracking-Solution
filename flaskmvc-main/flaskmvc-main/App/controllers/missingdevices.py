from datetime import datetime
from App.models import MissingDevice, AssetAssignment, Audit, Relocation
from App.database import db

def mark_asset_missing(audit_id, assignment_id):
    audit = Audit.query.get(audit_id)
    assignment = AssetAssignment.query.get(assignment_id)

    if not audit or not assignment:
        return None

    missing = MissingDevice(
        audit_id = audit_id,
        assignment_id = assignment_id,
        found_relocation_id = None,
        timestamp = datetime.utcnow()
    )

    db.session.add(missing)
    db.session.commit()

    return missing

def mark_asset_found(missing_id, relocation_id):
    missing = MissingDevice.query.get(missing_id)
    relocation = Relocation.query.get(relocation_id)
    
    if not missing or not relocation:
        return None

    missing.found_relocation_id = relocation_id
    
    db.session.commit()
    return missing

def get_all_missing():
    return MissingDevice.query.all()

def get_still_missing_devices(): # Retrieves all devices that are still missing
    return MissingDevice.query.filter(
        MissingDevice.found_relocation_id.is_(None)
    ).all()

def found_missing_devices(): # Retrieves all the devices that were missing but are now found
    return MissingDevice.query.filter(
        MissingDevice.found_relocation_id.isnot(None)
    ).all()