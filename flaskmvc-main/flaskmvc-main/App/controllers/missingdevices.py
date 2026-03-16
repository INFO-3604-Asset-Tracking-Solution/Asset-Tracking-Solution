from datetime import datetime
from App.models import MissingDevice, AssetAssignment, Audit 
from App.database import db

def mark_asset_missing(audit_id, assignment_id):
    audit = Audit.query.get(audit_id)
    assignment = AssetAssignment.query.get(assignment_id)

    if not audit or not assignment:
        return None

    missing = MissingDevice(
        audit_id = audit_id,
        assignment_id = assignment_id,
        found = None,
        timestamp = datetime.utcnow()
    )

    db.session.add(missing)
    db.session.commit()

    return missing

def mark_asset_found(missing_id, relocated_id):
    missing = MissingDevice.query.get(missing_id)
    
    if not missing:
        return None

    missing.found = relocated_id
    db.session.commit()

    return missing