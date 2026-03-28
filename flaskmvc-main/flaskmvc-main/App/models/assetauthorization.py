from App.models import db
from sqlalchemy import Enum
class AssetAuthorization(db.Model):
    __tablename__ = 'asset_authorizations'
    authorization_id = db.Column(db.Integer, primary_key=True)
    
    # Store asset details instead of a foreign key, because the asset DOES NOT exist in the Asset table yet.
    # When authorized, a new Asset will be created using these details. 
    description = db.Column(db.String(200), nullable=False)
    brand = db.Column(db.String(120), nullable=True)
    model = db.Column(db.String(120), nullable=True)
    serial_number = db.Column(db.String(50), nullable=True)
    cost = db.Column(db.Numeric(10, 2), nullable=True)
    notes = db.Column(db.String(300), nullable=True)
    status_id = db.Column(db.Integer, db.ForeignKey('assetstatus.status_id'), nullable=True) 

    proposing_user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    proposal_date = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    authorized_by = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=True)
    authorization_date = db.Column(db.DateTime, nullable=True)
    authorization_status = db.Column(Enum('Pending', 'Approved', 'Rejected', name='authorization_status_enum'), nullable=False, default='Pending')

    def __init__(self, description, proposing_user_id, brand=None, model=None, serial_number=None, cost=None, notes=None, status_id=None):
        self.description = description
        self.proposing_user_id = proposing_user_id
        self.brand = brand
        self.model = model
        self.serial_number = serial_number
        self.cost = cost
        self.notes = notes
        self.status_id = status_id
        self.authorization_status = 'Pending'

    def get_json(self):
        return {
            "authorization_id": self.authorization_id,
            "description": self.description,
            "brand": self.brand,
            "model": self.model,
            "serial_number": self.serial_number,
            "cost": float(self.cost) if self.cost else None,
            "notes": self.notes,
            "status_id": self.status_id,
            "proposing_user_id": self.proposing_user_id,
            "proposal_date": self.proposal_date.strftime('%Y-%m-%d %H:%M:%S') if self.proposal_date else None,
            "authorized_by": self.authorized_by,
            "authorization_date": self.authorization_date.strftime('%Y-%m-%d %H:%M:%S') if self.authorization_date else None,
            "authorization_status": self.authorization_status
        }