import unittest
from App.models import AssetAuthorization, Asset, Employee, AssetStatus
from App.controllers.assetauthorization import propose_asset, get_pending_authorizations, approve_asset
from App.database import db

class AuthorizationWorkflowIntegrationTests(unittest.TestCase):
    def setUp(self):
        db.session.query(AssetAuthorization).delete()
        db.session.query(Asset).delete()
        db.session.query(Employee).delete()
        db.session.commit()

        self.employee = Employee(first_name="Jane", last_name="Smith", email="jane@example.com")
        db.session.add(self.employee)
        
        self.admin = Employee(first_name="Admin", last_name="User", email="admin@example.com")
        db.session.add(self.admin)
        
        self.status = AssetStatus.query.filter_by(status_name="Available").first()
        if not self.status:
            self.status = AssetStatus(status_name="Available")
            db.session.add(self.status)
        db.session.commit()

    def test_authorization_workflow(self):
        # Step 1: User proposes a new asset
        proposal = propose_asset(
            description="MacBook Pro", 
            proposing_user_id=self.employee.employee_id, 
            brand="Apple", 
            model="M2 Max", 
            serial_number="APP123456", 
            cost=2500.0, 
            notes="For new developer",
            status_id=self.status.status_id
        )
        self.assertIsNotNone(proposal)
        self.assertEqual(proposal.authorization_status, "Pending")

        # Step 2: Admin views pending authorizations
        pending = get_pending_authorizations()
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0].authorization_id, proposal.authorization_id)

        # Step 3: Admin approves the asset
        new_asset = approve_asset(
            authorization_id=proposal.authorization_id, 
            authorized_by_user_id=self.admin.employee_id
        )
        self.assertIsNotNone(new_asset)
        
        # Step 4: Verify the asset was actually created in the DB
        self.assertEqual(new_asset.description, "MacBook Pro")
        self.assertEqual(new_asset.model, "M2 Max")
        
        # Verify the proposal status was updated
        updated_proposal = AssetAuthorization.query.get(proposal.authorization_id)
        self.assertEqual(updated_proposal.authorization_status, "Approved")
        self.assertEqual(updated_proposal.authorized_by, self.admin.employee_id)
