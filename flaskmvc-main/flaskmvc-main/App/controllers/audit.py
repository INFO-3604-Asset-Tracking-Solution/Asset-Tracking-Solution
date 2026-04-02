from App.models import Audit, CheckEvent, MissingDevice
from App.database import db
from datetime import datetime

def create_audit(initiator_id):

    # Check if there is already an active audit
    active_audit = Audit.query.filter(Audit.status.in_([ 'IN_PROGRESS', 'PENDING'])).first()
    if active_audit:
        return active_audit
        
    audit = Audit(
        initiator_id = initiator_id,
        start_date = datetime.utcnow(),
        end_date = None,
        status = "IN_PROGRESS"

    )
    db.session.add(audit)
    db.session.commit()

    return audit

def end_audit():
    
    # Get the currently active audit
    audit = Audit.query.filter(Audit.status.in_(['IN_PROGRESS', 'PENDING'])).first()

    if not audit:
        return None

    # Check for pending relocations
    pending_checks = CheckEvent.query.filter_by(audit_id=audit.audit_id, status='pending relocation').first()
    if pending_checks:
        return None # Can't close if pending relocation exists

    # Audit cannot finish without relocation table having all assets be relocated 
    
    audit.end_date = datetime.utcnow()
    audit.status = "COMPLETED"

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

def get_active_audit():
    return Audit.query.filter(Audit.status.in_(['IN_PROGRESS', 'PENDING'])).first()

def get_audit_status():
    audit = get_active_audit()
    if not audit:
        return 'NO_ACTIVE_AUDIT'
    return audit.get_json()['status']

def generate_interim_report(audit_id):
    audit = get_audit_by_id(audit_id)
    if not audit or audit.status != 'IN_PROGRESS':
        return None
    # Returns the four cases: 1) Asset is in the correct room, 2) Asset is in the wrong room, 3) Asset is missing, 4) Asset is in different condition
    
    # 1) Asset is in the correct room
    correct_room = CheckEvent.query.filter_by(audit_id=audit_id, status='correct room').all()
    # 2) Asset is in the wrong room
    wrong_room = CheckEvent.query.filter_by(audit_id=audit_id, status='wrong room').all()
    # 3) Asset is missing
    missing = CheckEvent.query.filter_by(audit_id=audit_id, status='missing').all()
    # 4) Asset is in different condition
    different_condition = CheckEvent.query.filter_by(audit_id=audit_id, status='different condition').all()
    
    return {
        'correct_room': [check_event.get_json() for check_event in correct_room],
        'wrong_room': [check_event.get_json() for check_event in wrong_room],
        'missing': [check_event.get_json() for check_event in missing],
        'different_condition': [check_event.get_json() for check_event in different_condition]
    }

def generate_final_report(audit_id):
    audit = get_audit_by_id(audit_id)
    if not audit:
        return None
    # Returns the four cases: 1) Asset is in the correct room, 2) Asset is in the wrong room, 3) Asset is missing, 4) Asset is in different condition
    
    # 1) Asset is in the correct room
    correct_room = CheckEvent.query.filter_by(audit_id=audit_id, status='correct room').all()
    # 2) Asset is in the wrong room
    wrong_room = CheckEvent.query.filter_by(audit_id=audit_id, status='wrong room').all()
    # 3) Asset is missing
    missing = CheckEvent.query.filter_by(audit_id=audit_id, status='missing').all()
    # 4) Asset is in different condition
    different_condition = CheckEvent.query.filter_by(audit_id=audit_id, status='different condition').all()
    
    return {
        'correct_room': [check_event.get_json() for check_event in correct_room],
        'wrong_room': [check_event.get_json() for check_event in wrong_room],
        'missing': [check_event.get_json() for check_event in missing],
        'different_condition': [check_event.get_json() for check_event in different_condition]
    }

    