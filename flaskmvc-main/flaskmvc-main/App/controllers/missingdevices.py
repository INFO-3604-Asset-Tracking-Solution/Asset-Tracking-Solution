from datetime import datetime
from App.models import MissingDevice, AssetAssignment, Audit, Relocation, Asset, AssetStatus
from App.database import db


def mark_asset_missing(audit_id, assignment_id):
    audit = Audit.query.get(audit_id)
    assignment = AssetAssignment.query.get(assignment_id)

    if not audit or not assignment:
        return None

    # Prevent duplicate open missing records for the same assignment in the same audit
    existing_missing = MissingDevice.query.filter_by(
        audit_id=audit_id,
        assignment_id=assignment_id,
        found_relocation_id=None
    ).first()

    if existing_missing:
        return existing_missing

    missing = MissingDevice(
        audit_id=audit_id,
        assignment_id=assignment_id
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


def mark_asset_lost(missing_id):
    missing = MissingDevice.query.get(missing_id)
    if not missing:
        return None

    assignment = AssetAssignment.query.get(missing.assignment_id)
    if not assignment:
        return None

    # End current assignment
    assignment.return_date = datetime.utcnow()

    # Update asset status to Lost
    asset = Asset.query.get(assignment.asset_id)
    if asset:
        lost_status = AssetStatus.query.filter_by(status_name="Lost").first()
        if not lost_status:
            lost_status = AssetStatus(status_name="Lost")
            db.session.add(lost_status)
            db.session.flush()

        asset.status_id = lost_status.status_id

    db.session.commit()
    return missing


def get_missing_by_id(missing_id):
    return MissingDevice.query.get(missing_id)


def get_all_missing():
    return MissingDevice.query.all()


def get_still_missing_devices():
    return MissingDevice.query.filter(
        MissingDevice.found_relocation_id.is_(None)
    ).all()


def found_missing_devices():
    return MissingDevice.query.filter(
        MissingDevice.found_relocation_id.isnot(None)
    ).all()


def get_still_missing_devices_json():
    records = get_still_missing_devices()
    return [record.get_json() for record in records]


def get_found_missing_devices_json():
    records = found_missing_devices()
    return [record.get_json() for record in records]