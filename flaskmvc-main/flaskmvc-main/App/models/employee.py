from App.database import db

class Employee(db.Model):

    __tablename__ = "employee"

    employee_id = db.Column(db.Integer, primary_key=True)
    employee_number = db.Column(db.String(20), unique=True, nullable=False) 
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=True)


    def __init__(self, employee_number, first_name, last_name=None, email=None):
        self.employee_number= employee_number
        self.first_name = first_name
        self.last_name = last_name
        self.email = email


    def get_json(self):
        return {
            'employee_id': self.employee_id,
            'employee_number': self.employee_number,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email
        }

    def __repr__(self):
        return f'<Assignee {self.first_name} {self.last_name}>'