import click, pytest, sys
from flask.cli import AppGroup
from App.database import db, get_migrate
from App.controllers.asset import *
from App.controllers.assetassignment import *
from App.controllers.audit import *
from App.controllers.employee import *
from App.controllers.relocation import *
from App.controllers.missingdevices import *
from App.controllers.room import *
from App.main import create_app
from App.controllers import ( create_user, get_all_users_json, get_all_users, initialize )
from App.models import Audit


# This commands file allow you to create convenient CLI commands for testing controllers

app = create_app()
migrate = get_migrate(app)

# This command creates and initializes the database
@app.cli.command("init", help="Creates and initializes the database")
def init():
    initialize()
    print('database intialized')

    #Add default asset statuses
    from App.controllers.assetstatus import create_asset_status

    create_asset_status("Available")
    create_asset_status("Assigned")
    create_asset_status("Under Maintenance")

    #Sample data for assets
    
    #Initialize csv 
    
       
    # filepath = 'CSVsample.csv' 
    # upload_csv(filepath)
    
        

'''
User Commands
'''

# Commands can be organized using groups

# create a group, it would be the first argument of the comand
# eg : flask user <command>
user_cli = AppGroup('user', help='User object commands') 

# Then define the command and any parameters and annotate it with the group (@)
@user_cli.command("create", help="Creates a user")
@click.argument("username") #default="rob"
@click.argument("password") #default="robpass"
@click.argument("role")
@click.argument("email")

def create_user_command(username, password, role, email):
    create_user(username, password, role, email)
    print(f'User {username} was Created!')

# this command will be : flask user create bob bobpass

@user_cli.command("list", help="Lists users in the database")
@click.argument("format")
def list_user_command(format):
    users = get_all_users_json()
    if format == 'json': 
        print(users)
    else:
        print(get_all_users())

app.cli.add_command(user_cli) # add the group to the cli


'''
Employee Commands
'''

employee_cli = AppGroup('employee', help = "Employee object command")

@employee_cli.command("create")
@click.argument("first_name")
@click.argument("last_name")
@click.argument("email")

def create_employee_command(first_name, last_name, email):
    emp = create_employee(first_name, last_name, email)
    if emp:
        print(f"Employee {emp.employee_id}: {emp.first_name} {emp.last_name} was Created")
    else:
        print("Error creating employee")

@employee_cli.command("list", help= "List all employees")
def list_employees():
    employees = get_all_employees()
    if not employees:
        print("No employees found")
        return
    print(f"{'ID':>3} | {'First Name':<12} {'Last Name':<12} | Email")
    print("-" * 55)
    for e in employees:
        print(f"{e.employee_id:>3}: {e.first_name:<12} {e.last_name:<12} - {e.email}")

app.cli.add_command(employee_cli)


'''
Asset Commands
'''
asset_cli = AppGroup('asset', help="Asset object commands")

@asset_cli.command("create", help="creates an asset")
@click.argument("asset_id") #default= ""
@click.argument("description") #default=""
@click.argument("brand") #default=""
@click.argument("model") #default=""
@click.argument("serial_number") #default="00000000"
@click.argument("cost") #default="Good Condition"
@click.argument("notes") #default=""
@click.argument("status_name", default= "Available")
#@click.argument("last_update") default="02/02/2002"

def add_asset_command(asset_id, description, brand, model, serial_number, cost, notes, status_name):
    asset = add_asset(asset_id, description, brand, model, serial_number, cost, notes, status_name)
    if asset is None:
        print('Error creating asset')
    else:
        print(f'Asset {asset.asset_id} was Created!')

@asset_cli.command("list", help ="List all assets")
def list_assets():
    assets = get_all_assets()
    if not assets:
        print("No Assets Found")
        return        
        
    print(f"{'ID':>3} | {'Description':<15} | {'Brand':<10} | {'Model':<10} | {'Serial Model':<10} | {'Cost':<10} | {'Status Name':<10}")
    print("-" * 60)

    for a in assets:
        #Get the status name
        status_name = a.status.status_name if a.status else "Unknown"
        cost_display = f"{float(a.cost):.2f}" if a.cost else "0.00"
        print(f"{a.asset_id:>3} | {a.description:<15} | {a.brand:<10} | {a.model:<10} | {a.serial_number:<12} | {cost_display:<10} | {status_name:<15}")

app.cli.add_command(asset_cli) # add the group to the cli


check_event_cli = AppGroup('checkevent', help= "CheckEvent object commands")

@check_event_cli.command("create", help = "Creates a check event")
@click.argument("audit_id")
@click.argument("asset_id")
@click.argument("user_id")
@click.argument("found_room_id")
@click.argument("condition_id")

def create_check_event_command(audit_id, asset_id, user_id, found_room_id, condition_id):
    event = create_check_event(audit_id, asset_id, user_id, found_room_id, condition_id) 
    if event:
        print(f"Check Event {event.id} was Successfully Created!")
    else:
        print(f"Error Creating Check Event")

@check_event_cli.command("list") #help="Lists all check events for an audit"
@click.argument("audit_id")
@click.argument("format", default="string")
def list_check_event_command(audit_id, format):
    if format == "string":
        events = get_all_check_events_by_audit(audit_id)
        if not events:
            print("No check events found for this audit.")
        else:
            for e in events:
                print(f"CheckEvent {e.id}: Asset {e.asset_id}, User {e.user_id}, Room {e.found_room_id}, Condition {e.condition_id}, Time {e.timestamp}")

            else:
                print(get_all_check_events_by_audit_json(audit_id))


app.cli.add_command(check_event_cli)


'''
Audit Commands
'''
audit_cli = AppGroup('audit', help="Audit object commands")

@audit_cli.command("create", help="creates an audit")
@click.argument("initiator_id") 

def add_audit_commands(initiator_id):
    audit = create_audit(initiator_id)

    if audit is None:
        print('Error creating audit')
    else:
        print(f'Audit {audit.audit_id} was Created!')

@audit_cli.command("list", help="List all audits")
def list_audits():
    audits = Audit.query.all()

    if not audits:
        print("No audits found")
        return

    print(f"{'ID':<10} | {'Initiator':<10} | {'Status':<15} | {'Start Date':<20} | {'End Date':<20} ")
    print("-" * 50)

    for a in audits:
        start = a.start_date.strftime("%Y-%m-%d %H:%M") if a.start_date else "N/A"
        end = a.end_date.strftime("%Y-%m-%d %H:%M") if a.end_date else "N/A"
        print(f"{a.audit_id:<10} | {a.initiator_id:<10} | {a.status:<15} | {start:<20} | {end:<20}")

@audit_cli.command("end", help="Ends an audit")
@click.argument("audit_id")

def end_audit_command(audit_id):
    audit = end_audit(audit_id)

    if not audit:
        print("Audit not found")
    else:
        print(f"Audit {audit.audit_id} completed at {audit.end_date}")


app.cli.add_command(audit_cli)

'''
Test Commands
'''

test = AppGroup('test', help='Testing commands') 

@test.command("run", help="Run tests by type or module")
@click.argument("category", default="all")
def user_tests_command(category):
    if category == "unit":
        args = ["App/tests/unit"]
    elif category == "int":
        args = ["App/tests/integration"]
    elif category in ["user", "asset", "assignee", "location_hierarchy", "asset_assignment", "scanevent"]:
        args = [f"App/tests/integration/test_int_{category}.py"]
    else:
        args = ["App/tests"]
    pytest.main(args + ["-v"])
    

app.cli.add_command(test)