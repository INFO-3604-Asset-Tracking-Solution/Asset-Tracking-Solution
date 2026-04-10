from App.models import Relocation, CheckEvent, Room
from App.database import db
from App.controllers.assetassignment import get_current_asset_assignment, end_assignment, create_asset_assignment



def create_relocation(check_id, found_room_id):
    check = CheckEvent.query.get(check_id)
    room = Room.query.get(found_room_id)

    if not check or not room:
        return None
    if check.status != 'pending relocation':
        return None

    existing = Relocation.query.filter_by(check_id=check_id).first()
    if existing:
        return existing

    relocation = Relocation(
        check_id=check_id,
        found_in_id=found_room_id,
    )

    db.session.add(relocation)
    db.session.commit()

    return relocation


def resolve_relocation_extended(relocation_id, choice, new_room_id=None):
    """
    Handles complex relocation resolutions.
    Choices: 'reassign', 'return_home', 'end_assignment'
    """
    relocation = get_relocation(relocation_id)
    if not relocation:
        return None

    check = CheckEvent.query.get(relocation.check_id)
    if not check:
        return None

    asset_id = check.asset_id
    current_assignment = get_current_asset_assignment(asset_id)

    if choice == 'reassign' and new_room_id:
        # 1. End current assignment if exists
        if current_assignment:
            end_assignment(current_assignment.assignment_id)
        
        # 2. Create new assignment to the new room (where found or chosen)
        # For simplicity, we assign it to the employee from previous assignment if exists
        prev_emp_id = current_assignment.employee_id if current_assignment else 1 # Fallback to admin/system employee if needed
        create_asset_assignment(asset_id, prev_emp_id, new_room_id, check.condition)
        
        # 3. Create success check event and link
        new_check = CheckEvent(
            audit_id=check.audit_id,
            asset_id=asset_id,
            user_id=check.user_id,
            found_room_id=new_room_id,
            condition=check.condition,
            status='relocated'
        )
        db.session.add(new_check)
        db.session.flush()
        relocation.new_check_event_id = new_check.check_id
        check.status = 'relocated'

    elif choice == 'return_home':
        # Don't change assignment. Just acknowledge it needs to go back.
        # We don't mark as resolved in the DB fully (new_check_event_id stays None)
        # so it stays in the list, but we could add a note.
        # However, the user said "remain in the list", so we just exit.
        print(f"Relocation {relocation_id} marked for return home.")
        pass

    elif choice == 'end_assignment':
        # 1. End current assignment
        if current_assignment:
            end_assignment(current_assignment.assignment_id)
        
        # 2. Mark relocation as resolved by concluding it
        check.status = 'relocated' # Or maybe a new status, but 'relocated' works for UI filters
        # We create a new check event in its "found" room but with no assignment
        new_check = CheckEvent(
            audit_id=check.audit_id,
            asset_id=asset_id,
            user_id=check.user_id,
            found_room_id=check.found_room_id,
            condition=check.condition,
            status='found' # It's found and now "Available"
        )
        db.session.add(new_check)
        db.session.flush()
        relocation.new_check_event_id = new_check.check_id

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
    and creates a new check event for the relocated item
    """
    relocation = get_relocation(relocation_id)
    if not relocation:
        return None

    check = CheckEvent.query.get(relocation.check_id)
    room = Room.query.get(item_relocated_room_id)

    if not check or not room:
        return None

    new_check_row = CheckEvent.query.get(relocation.new_check_event_id) if relocation.new_check_event_id else None
    if new_check_row:
        new_check_row.found_room_id = item_relocated_room_id
        new_check_row.condition = check.condition
        new_check_row.status = 'relocated'
    else:
        new_check_row = CheckEvent(
            audit_id=check.audit_id,
            asset_id=check.asset_id,
            user_id=check.user_id,
            found_room_id=item_relocated_room_id,
            condition=check.condition,
            status='relocated'
        )
        db.session.add(new_check_row)
        db.session.flush()  # get check_id for new row
        relocation.new_check_event_id = new_check_row.check_id

    check.status = 'relocated'

    db.session.commit()

    return relocation