from App.database import db
from datetime import datetime

class MissingDevice(db.Model):
    __tablename__ = 'missing_device'

    missing_id = db.Column(db.String(30), primary_key=True)
    audit_id = db.Column(db.String(30), db.ForeignKey('audit.id'), nullable=False)
    asset_id = db.Column(db.String(30), db.ForeignKey('asset.asset_id'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(20), nullable=False) 
    found_relocation_id = db.Column(db.String(30), db.ForeignKey('relocation.relocation_id'), nullable=True)

    asset = db.relationship('Asset', backref='missing_records', lazy=True)

    def __init__(self, missing_id, audit_id, asset_id, status, found_relocation_id=None, date=None):
        self.missing_id = missing_id
        self.audit_id = audit_id
        self.asset_id = asset_id
        self.status = status
        self.found_relocation_id = found_relocation_id
        self.date = date if date else datetime.utcnow()