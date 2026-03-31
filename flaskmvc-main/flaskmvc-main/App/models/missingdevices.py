from App.database import db
from datetime import datetime

class MissingDevice(db.Model):
    __tablename__ = 'missing_device'

    missing_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    audit_id = db.Column(db.String(30), db.ForeignKey('audit.audit_id'), nullable=False)
    assignment_id = db.Column(db.String(30), db.ForeignKey('asset_assignment.assignment_id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    found_relocation_id = db.Column(db.String(30), db.ForeignKey('relocation.relocation_id'), nullable=True)

    # asset = db.relationship('Asset', backref='missing_records', lazy=True)

    def __init__(self, audit_id, assignment_id, timestamp=None):
        self.audit_id = audit_id
        self.assignment_id = assignment_id
        self.timestamp = timestamp if timestamp else datetime.utcnow()


    def get_json(self):
        return {
            'missing_id': self.missing_id,
            'audit_id': self.audit_id,
            'assignment_id': self.assignment_id,
            'timestamp': self.timestamp,
            'found_relocation_id': self.found_relocation_id
        }