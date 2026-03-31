from App.database import db
from datetime import datetime
from nanoid import generate

def generate_short_id():
    return generate(size=10)

class Relocation(db.Model):
    __tablename__ = 'relocation'

    relocation_id = db.Column(db.String(30), primary_key=True, default=generate_short_id)
    check_id = db.Column(db.String(30), db.ForeignKey('checkevent.check_id'), nullable=False)
    found_in_room_id = db.Column(db.Integer, db.ForeignKey('room.room_id'), nullable=False)
    item_relocated_id = db.Column(db.Integer, db.ForeignKey('checkevent.check_id'), nullable=True) # New location of item after relocation - Check event table
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __init__(self, check_id, found_in_room_id):
        self.check_id = check_id
        self.found_in_room_id = found_in_room_id
        self.item_relocated_id = None

    def get_json(self):
        return {
            'relocation_id': self.relocation_id,
            'check_id': self.check_id,
            'found_in_room_id': self.found_in_room_id,
            'item_relocated_id': self.item_relocated_id,
            'timestamp': self.timestamp.isoformat()
        }