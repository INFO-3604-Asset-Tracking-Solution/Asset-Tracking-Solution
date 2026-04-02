from App.models import CheckEvent, Audit, Asset
from App.database import db
from datetime import datetime
from App.controllers.assetassignment import get_asset_assignment_by_id, get_current_asset_assignment


def create_check_event(audit_id, asset_id, user_id, found_room_id, condition_id, status='found'):

    audit = Audit.query.get(audit_id)
    asset = Asset.query.get(asset_id)

    if not audit or not asset:
        return None

    if audit.status == "COMPLETED":
        return None

    check_event = CheckEvent(
        audit_id=audit_id,
        asset_id=asset_id,
        user_id=user_id,
        found_room_id=found_room_id,
        condition=condition_id,
        status=status
    )

    db.session.add(check_event)
    db.session.commit()

    return check_event

def get_all_check_events_by_audit(audit_id):
    return CheckEvent.query.filter_by(audit_id = audit_id).all()

def get_all_check_events_by_audit_json(audit_id):
    events = get_all_check_events_by_audit(audit_id)

    if not events:
        return []

    return [event.get_json() for event in events]

def check_event_location_discrepancy(check_event):
    asset_assignment = get_current_asset_assignment(check_event.asset_id)
    if asset_assignment.room_id != check_event.found_room_id:
        return True
    return False

def check_event_condition_discrepancy(check_event):
    asset_assignment = get_current_asset_assignment(check_event.asset_id)
    if asset_assignment.condition != check_event.condition:
        return True
    return False
    
def get_check_event(check_id):
    return CheckEvent.query.get(check_id)

def update_check_event_condition(check_id, condition):
    check_event = CheckEvent.query.get(check_id)
    if not check_event:
        return None
    
    check_event.condition = condition
    db.session.commit()
    return check_event
