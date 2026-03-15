from App.models import Audit
from App.database import db
from datetime import datetime

def create_audit(initiator_id):
    audit = Audit(
        initiator_id = initiator_id,
        start_date = datetime.utcnow(),
        end_date = None,
        status = "IN_PROGRESS"

    )
    db.session.add(audit)
    db.session.commit()

    return audit

def end_audit(audit_id):
    audit = Audit.query.get(audit_id)

    if not audit:
        return None

    if audit.status == "COMPLETED":
        return audit

    audit.end_date = datetime.utcnow():
    audit.status = "COMPLETED"

    db.session.commit()

    return audit

