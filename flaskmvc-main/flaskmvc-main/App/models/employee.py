from App.database import db

class Employee(db.Model):

    __tablename__ = "employee"

    employee_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)


    def __init__(self, first_name, last_name, email):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email


    def get_json(self):
        return {
            'id': self.employee_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email
        }

    def __repr__(self):
        return f'<Employee {self.first_name} {self.last_name} {self.email}>' 