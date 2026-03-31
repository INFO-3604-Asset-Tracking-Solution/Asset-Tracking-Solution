from App.database import db
from datetime import datetime
from nanoid import generate

def generate_short_id():
    return generate(size=10)

class Relocation(db.Model):
    __tablename__ = 'relocation'

    relocation_id = db.Column(db.String(30), primary_key=True, default=generate_short_id)
    check_id = db.Column(db.String(30), db.ForeignKey('checkevent.check_id'), nullable=False)
    found_in_id = db.Column(db.Integer, db.ForeignKey('room.room_id'), nullable=False)
    new_check_event_id = db.Column(db.String(30), db.ForeignKey('checkevent.check_id'), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # audit = db.relationship('Audit', backref='relocations', lazy=True)
    missing_devices_found = db.relationship('MissingDevice', backref='found_relocation', lazy=True)

    def __init__(self, check_id, found_in_id, new_check_event_id=None):
        self.check_id = check_id
        self.found_in_id = found_in_id
        self.new_check_event_id = new_check_event_id

    def get_json(self):
        return {
            'relocation_id': self.relocation_id,
            'check_id': self.check_id,
            'found_in_id': self.found_in_id,
            'timestamp': self.timestamp.isoformat()
        }