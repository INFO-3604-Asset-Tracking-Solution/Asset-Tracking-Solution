from App.models import Audit, CheckEvent, MissingDevice
from App.database import db
from datetime import datetime

def create_audit(initiator_id):

    # Check if there is already an active audit
    active_audit = Audit.query.filter(Audit.status.in_([ 'in_progress', 'pending'])).first()
    if active_audit:
        return active_audit
        
    audit = Audit(
        initiator_id = initiator_id,
        start_date = datetime.utcnow(),
        end_date = None,
        status = "in_progress"

    )
    db.session.add(audit)
    db.session.commit()

    return audit

def end_audit():
    
    # Get the currently active audit
    audit = Audit.query.filter(Audit.status.in_(['in_progress', 'pending'])).first()

    if not audit:
        return None

    # Check for pending relocations
    pending_checks = CheckEvent.query.filter_by(audit_id=audit.audit_id, status='pending relocation').first()
    if pending_checks:
        return None # Can't close if pending relocation exists

    # Mark still missing devices as 'lost' in CheckEvents
    # Actually, we need to find missing devices and update their corresponding check event status, 
    # but missing devices might not have check events yet. Let's create 'lost' check events for them, 
    # or update them appropriately. 

    still_missing = MissingDevice.query.filter_by(audit_id=audit.audit_id, found_relocation_id=None).all()
    for missing in still_missing:
        # Check if there is already a CheckEvent for this assignment/asset
        asset_id = missing.assignment.asset_id if missing.assignment else None
        if asset_id:
            check_event = CheckEvent.query.filter_by(audit_id=audit.audit_id, asset_id=asset_id).first()
            if check_event:
                check_event.status = 'lost'
            else:
                # Assuming 'lost' implies we log a check event saying it's lost
                check_event = CheckEvent(
                    audit_id=audit.audit_id,
                    asset_id=asset_id,
                    user_id=audit.initiator_id, # Or some default user
                    found_room_id=missing.assignment.room_id if missing.assignment else 0, # They weren't found, use expected room
                    condition='Good', # Place holder
                    status='lost'
                )
                db.session.add(check_event)

    audit.end_date = datetime.utcnow()
    audit.status = "completed"

    db.session.commit()

    return audit

def get_all_audits():
    return Audit.query.all()

def get_all_audits_json():
    audits = get_all_audits()
    if not audits:
        return[]
    audits = [audit.get_json() for audit in audits]
    return audits

def get_audit_by_id(audit_id):
    return Audit.query.filter_by(audit_id=audit_id).first()

def get_audit_by_initiator_id(initiator_id):
    return Audit.query.filter_by(initiator_id=initiator_id).all()

def get_audit_by_status(status):
    return Audit.query.filter_by(status=status).all()

def get_audit_by_date_range(start_date, end_date):
    return Audit.query.filter(Audit.start_date >= start_date, Audit.end_date <= end_date).all()

def get_audit_by_date(date):
    return Audit.query.filter(Audit.start_date <= date, Audit.end_date >= date).first()
