import unittest
from App.models import Employee
from App.controllers.employee import (
    create_employee, get_employee_by_id, 
    update_employee, get_all_employees
)
from App.database import db

class EmployeeIntegrationTests(unittest.TestCase):
    def setUp(self):
        db.session.query(Employee).delete()
        db.session.commit()

    def test_create_employee(self):
        emp = create_employee("John", "Doe", "john.doe@example.com")
        self.assertIsNotNone(emp)
        self.assertIsNotNone(emp.employee_id)
        self.assertEqual(emp.first_name, "John")

    def test_get_employee(self):
        emp = create_employee("Jane", "Smith", "jane.smith@example.com")
        fetched = get_employee_by_id(emp.employee_id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.last_name, "Smith")
        
    def test_get_all_employees(self):
        create_employee("Emp1", "L1", "e1@a.com")
        create_employee("Emp2", "L2", "e2@a.com")
        employees = get_all_employees()
        self.assertEqual(len(employees), 2)
