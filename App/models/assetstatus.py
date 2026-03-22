from App.database import db

class AssetStatus(db.Model):

    __tablename__ = "assetstatus"

    status_id = db.Column(db.Integer, primary_key=True)
    status_name = db.Column(db.String(50), nullable=False, unique=True)

    assets = db.relationship('Asset', backref='status', lazy=True)


    def __init__(self, status_name):
        self.status_name = status_name


    def get_json(self):
        return {
            "status_id": self.status_id,
            "status_name": self.status_name,
        }