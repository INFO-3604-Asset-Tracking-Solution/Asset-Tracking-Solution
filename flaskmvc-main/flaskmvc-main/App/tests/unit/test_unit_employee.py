import unittest
from App.models import Employee

class EmployeeUnitTests(unittest.TestCase):

    def test_new_employee(self):
        employee = Employee("John", "Doe", "john.doe@example.com")
        self.assertEqual(employee.first_name, "John")
        self.assertEqual(employee.last_name, "Doe")
        self.assertEqual(employee.email, "john.doe@example.com")

    def test_employee_get_json(self):
        employee = Employee("Jane", "Smith", "jane.smith@example.com")
        # employee_id is None since it's not saved to DB
        expected_json = {
            'id': None,
            'first_name': "Jane",
            'last_name': "Smith",
            'email': "jane.smith@example.com"
        }
        self.assertDictEqual(employee.get_json(), expected_json)

    def test_employee_repr(self):
        employee = Employee("Bob", "Ross", "bob.ross@example.com")
        self.assertEqual(repr(employee), "<Employee Bob Ross bob.ross@example.com>")
