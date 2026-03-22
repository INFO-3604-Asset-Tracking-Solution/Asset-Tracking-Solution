from App.models import Employee
from App import db
import re

def create_employee(first_name, last_name=None, email=None):
    if email and Employee.query.filter_by(email=email).first():
        print(f"Warning: Email {email} already exists. Cannot create duplicate.")
        return None

    new_employee = Employee(fname=first_name, lname=last_name, email=email)

    try:
        db.session.add(new_employee)
        db.session.commit()
        return new_employee
    except Exception as e:
        db.session.rollback()
        print(f"Error creating employee: {e}")
        return None


def get_employee_by_id(employee_id):
    try:
        return Employee.query.get(int(employee_id))
    except (ValueError, TypeError):
        return None


def get_employee_by_first_name(first_name):
    return Employee.query.filter_by(first_name=first_name).all()


def get_employee_by_last_name(last_name):
    return Employee.query.filter_by(last_name=last_name).all()


def get_employee_by_email(email):
    if not email:
        return None
    return Employee.query.filter(db.func.lower(Employee.email) == email.lower()).first()


def get_all_employees():
    return Employee.query.all()


def get_all_employees_json():
    employees = Employee.query.all()
    if not employees:
        return []
    employees = [employee.get_json() for employee in employees]
    return employees


def update_employee(employee_id, first_name, last_name, email):
    employee = get_employee_by_id(employee_id)

    if employee:
        employee.first_name = first_name
        employee.last_name = last_name
        employee.email = email

        try:
            db.session.commit()
            return employee
        except Exception as e:
            db.session.rollback()
            print(f"Error updating employee: {e}")
            return None

    return None


def get_or_create_employee_by_name(full_name):
    if not full_name or not full_name.strip():
        return None

    name_parts = full_name.strip().split(maxsplit=1)
    first_name = name_parts[0]
    last_name = name_parts[1] if len(name_parts) > 1 else None

    existing_employee = None

    if last_name:
        existing_employee = Employee.query.filter(
            db.func.lower(Employee.first_name) == first_name.lower(),
            db.func.lower(Employee.last_name) == last_name.lower()
        ).first()
    else:
        existing_employee = Employee.query.filter(
            db.func.lower(Employee.first_name) == first_name.lower(),
            Employee.last_name.is_(None)
        ).first()

    if existing_employee:
        return existing_employee
    else:
        safe_first = re.sub(r'\W+', '', first_name.lower())
        safe_last = re.sub(r'\W+', '', last_name.lower()) if last_name else ''

        if last_name:
            placeholder_email = f"{safe_first}.{safe_last}.placeholder@auto.generated"
        else:
            placeholder_email = f"{safe_first}.placeholder@auto.generated"

        counter = 1
        temp_email = placeholder_email

        while get_employee_by_email(temp_email):
            if last_name:
                temp_email = f"{safe_first}.{safe_last}{counter}.placeholder@auto.generated"
            else:
                temp_email = f"{safe_first}{counter}.placeholder@auto.generated"
            counter += 1

        placeholder_email = temp_email

        print(f"Creating new employee: {first_name} {last_name or ''} with email {placeholder_email}")
        new_employee = create_employee(first_name=first_name, last_name=last_name, email=placeholder_email)
        return new_employee