from App.database import db
from datetime import datetime

class Relocation(db.Model):
    __tablename__ = 'relocation'

    relocation_id = db.Column(db.String(30), primary_key=True)
    audit_id = db.Column(db.String(30), db.ForeignKey('audit.id'), nullable=False)
    assignment_id = db.Column(db.String(30), db.ForeignKey('assignment.assignment_id'), nullable=False)
    found_in_id = db.Column(db.String(30), nullable=False) 
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(20), nullable=False) 

    assignment = db.relationship('Assignment', backref='relocations', lazy=True)
    audit = db.relationship('Audit', backref='relocations', lazy=True)
    missing_devices_found = db.relationship('MissingDevice', backref='found_relocation', lazy=True)

    def __init__(self, relocation_id, audit_id, assignment_id, found_in_id, status, date=None):
        self.relocation_id = relocation_id
        self.audit_id = audit_id
        self.assignment_id = assignment_id
        self.found_in_id = found_in_id
        self.status = status
        self.date = date if date else datetime.utcnow()