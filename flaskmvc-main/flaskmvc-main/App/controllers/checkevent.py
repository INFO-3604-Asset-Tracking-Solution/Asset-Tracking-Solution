from App.models import CheckEvent, Audit, Asset
from App.database import db
from datetime import datetime


def create_check_event(audit_id, asset_id, user_id, found_room_id, condition_id, status='found'):

    audit = Audit.query.get(audit_id)
    asset = Asset.query.get(asset_id)

    if not audit or not asset:
        return None

    if audit.status == "completed":
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