from App.database import db
from sqlalchemy import Numeric
from nanoid import generate

def generate_short_id():
    return generate(size=8)

class Asset(db.Model):

    __tablename__ = "asset"

    asset_id = db.Column(db.String(50), primary_key=True, default=generate_short_id)
    description = db.Column(db.String(200), nullable=True) 
    brand = db.Column(db.String(120), nullable=True)
    model = db.Column(db.String(120), nullable=True)
    serial_number = db.Column(db.String(50), nullable=True)
    status_id = db.Column(db.Integer, db.ForeignKey('assetstatus.status_id'), nullable=False)
    cost = db.Column(Numeric(10, 2), nullable=True)
    notes = db.Column(db.String(300), nullable=True)
    last_update = db.Column(db.DateTime, default=db.func.current_timestamp())

    checkevents = db.relationship('CheckEvent', backref='asset', lazy=True)
    assignments = db.relationship('AssetAssignment', backref='asset', lazy=True)

    def __init__(self, description, brand=None, model=None, serial_number=None, status_id=None, cost=None, notes=None):
        self.description = description
        self.brand = brand
        self.model = model
        self.serial_number = serial_number
        self.status_id = status_id
        self.cost = cost
        self.notes = notes

    def get_json(self):
        return {
            "asset_id": self.asset_id,
            "description": self.description,
            "brand": self.brand,
            "model": self.model,
            "serial_number": self.serial_number,
            "status_id": self.status_id,
            "cost": float(self.cost) if self.cost else None,
            "notes": self.notes,
            "last_update": self.last_update
        }