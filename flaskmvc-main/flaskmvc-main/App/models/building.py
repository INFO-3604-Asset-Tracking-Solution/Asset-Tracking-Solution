from App.database import db

class Building(db.Model):
    __tablename__ = 'building'
    building_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    building_name = db.Column(db.String(50), nullable=False)

    floors = db.relationship('Floor', backref='building', lazy=True, cascade="all, delete-orphan")

    def __init__(self, building_name):
        self.building_name = building_name

    def get_json(self):
        return {
            'building_id': self.building_id,
            'building_name': self.building_name
        }

    def __repr__(self):
        return f'<Building {self.building_id}: {self.building_name}>'
