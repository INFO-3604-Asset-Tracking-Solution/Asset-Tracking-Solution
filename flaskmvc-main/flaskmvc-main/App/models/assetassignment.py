from App.database import db
from datetime import datetime
from nanoid import generate
from sqlalchemy import Enum

def generate_assignment_id():
    return generate(size=10)

class AssetAssignment(db.Model):
    __tablename__ = "asset_assignment"

    assignment_id = db.Column(db.String(30), primary_key=True, default=generate_assignment_id)
    asset_id = db.Column(db.String(50), db.ForeignKey('asset.asset_id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.employee_id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.room_id'), nullable=False)
    assignment_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    return_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.Enum('Active', 'Completed', name='assignment_status'), default='Active', nullable=False)
    condition = db.Column(
        Enum('Good', 'Needs Repair', 'Beyond Repair', name='condition_enum'),
        nullable=False
    )
    
    # asset = db.relationship('Asset', backref='assignments', lazy=True)
    employee = db.relationship('Employee', backref='assignments', lazy=True)
    # room = db.relationship('Room', backref='assignments', lazy=True)

    def __init__(self, asset_id, employee_id,
     room_id, condition, assignment_date=None, return_date=None):
        self.asset_id = asset_id
        self.employee_id = employee_id
        self.room_id = room_id
        self.condition = condition
        self.assignment_date = assignment_date if assignment_date else datetime.utcnow()
        self.return_date = return_date
  
    def get_json(self):
        return {
            'assignment_id': self.assignment_id,
            'asset_id': self.asset_id,
            'employee_id': str(self.employee_id).zfill(8) if self.employee_id else '',
            'room_id': str(self.room_id).zfill(4) if self.room_id else '',
            'assignment_date': self.assignment_date,
            'return_date': self.return_date,
            'condition': self.condition,
        }

    def __repr__(self):
        return f"<AssetAssignment {self.assignment_id}>"

    def __str__(self):
        return f'Assignment {self.assignment_id} (Asset: {self.asset_id}, Employee: {self.employee_id}, Room: {self.room_id}, Condition: {self.condition})'