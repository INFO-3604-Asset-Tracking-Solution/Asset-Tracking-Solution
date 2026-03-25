from App.database import db
from datetime import datetime
from nanoid import generate

def generate_short_id():
    return generate(size=8)

class AssetAssignment(db.Model):
    __tablename__ = "asset_assignment"

    assignment_id = db.Column(db.String(30), primary_key=True, default=generate_short_id)
    asset_id = db.Column(db.String(50), db.ForeignKey('asset.asset_id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.employee_id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.room_id'), nullable=False)
    assignment_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    return_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.Enum('in_use', 'returned', name='assignment_status'), default='in_use', nullable=False)
    
    # asset = db.relationship('Asset', backref='assignments', lazy=True)
    employee = db.relationship('Employee', backref='assignments', lazy=True)
    # room = db.relationship('Room', backref='assignments', lazy=True)

    def __init__(self, asset_id, employee_id, room_id, assignment_date=None, return_date=None):
        self.asset_id = asset_id
        self.employee_id = employee_id
        self.room_id = room_id

        self.assignment_date = assignment_date if assignment_date else datetime.utcnow()
        self.return_date = return_date
        self.status = 'returned' if return_date else 'in_use'

    def get_json(self):
        return {
            'assignment_id': self.assignment_id,
            'asset_id': self.asset_id,
            'employee_id': self.employee_id,
            'room_id': self.room_id,
            'assignment_date': self.assignment_date,
            'return_date': self.return_date,
            'status': self.status
        }

    def __repr__(self):
        return f"<AssetAssignment {self.assignment_id}>"

    def __str__(self):
        return f'Assignment {self.assignment_id} (Asset: {self.asset_id}, Employee: {self.employee_id}, Room: {self.room_id})'