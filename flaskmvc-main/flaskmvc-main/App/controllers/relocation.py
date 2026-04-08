from App.models import Relocation, CheckEvent, Room
from App.database import db


def create_relocation(check_id, found_room_id):
    check = CheckEvent.query.get(check_id)
    room = Room.query.get(found_room_id)

    if not check or not room:
        return None

    # Idempotency guard: if unresolved relocation exists for this check, reuse it
    existing = Relocation.query.filter_by(
        check_id=check_id,
        new_check_event_id=None
    ).first()
    if existing:
        return existing

    relocation = Relocation(
        check_id=check_id,
        found_in_id=found_room_id,
    )

    db.session.add(relocation)
    db.session.commit()

    return relocation

def get_all_relocations():
    return Relocation.query.all()


def get_relocation(relocation_id):
    return Relocation.query.get(relocation_id)


def get_relocation_by_check(check_id):
    return Relocation.query.filter_by(check_id=check_id).all()


def update_relocation(relocation_id, item_relocated_room_id):
    """
    Updates the relocation with the new room id
    and creates a new check event for the relocated item.
    """
    relocation = get_relocation(relocation_id)
    if not relocation:
        return None

    # Already resolved: idempotent return
    if relocation.new_check_event_id:
        return relocation

    check = CheckEvent.query.get(relocation.check_id)
    room = Room.query.get(item_relocated_room_id)

    if relocation.new_check_event_id:
        return relocation

    if not check or not room:
        return None

    new_check_row = CheckEvent(
        audit_id=check.audit_id,
        asset_id=check.asset_id,
        user_id=check.user_id,
        found_room_id=item_relocated_room_id,
        condition=check.condition,
        status='relocated'
    )

    check.status = 'relocated'

    db.session.add(new_check_row)
    db.session.flush()  # get check_id for new row
    relocation.new_check_event_id = new_check_row.check_id
    db.session.commit()

    return relocation