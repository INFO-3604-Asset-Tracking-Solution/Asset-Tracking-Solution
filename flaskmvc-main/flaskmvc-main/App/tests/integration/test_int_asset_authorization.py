import unittest
from datetime import datetime
from App.models import AssetAuthorization, User, Asset, AssetStatus
from App.controllers.assetauthorization import (
    propose_asset, approve_asset, reject_asset, 
    get_pending_authorizations, delete_proposal
)
from App.controllers.user import create_user
from App.controllers.assetstatus import create_asset_status
from App.database import db

class AssetAuthorizationIntegrationTests(unittest.TestCase):
    def setUp(self):
        db.session.query(AssetAuthorization).delete()
        db.session.query(Asset).delete()
        db.session.query(User).delete()
        db.session.commit()

        # Ensure 'Available' status exists
        self.status = AssetStatus.query.filter_by(status_name="Available").first()
        if not self.status:
            self.status = create_asset_status("Available")
        
        self.proposer = create_user("proposer@test.com", "proposer", "pass", "Auditor")
        self.manager = create_user("manager@test.com", "manager", "pass", "Manager")

    def test_propose_asset(self):
        proposal = propose_asset(
            description="MacBook Pro",
            proposing_user_id=self.proposer.user_id,
            brand="Apple",
            model="M2",
            serial_number="APP123",
            cost=2000.0
        )
        self.assertIsNotNone(proposal)
        self.assertEqual(proposal.authorization_status, 'Pending')
        
    def test_approve_asset(self):
        proposal = propose_asset("Monitor", self.proposer.user_id, cost=300)
        new_asset = approve_asset(proposal.authorization_id, self.manager.user_id)
        
        self.assertIsNotNone(new_asset)
        self.assertEqual(new_asset.description, "Monitor")
        
        # Check proposal status
        updated_proposal = AssetAuthorization.query.get(proposal.authorization_id)
        self.assertEqual(updated_proposal.authorization_status, 'Approved')
        self.assertEqual(updated_proposal.authorized_by, self.manager.user_id)

    def test_reject_asset(self):
        proposal = propose_asset("Gaming PC", self.proposer.user_id, cost=5000)
        rejected = reject_asset(proposal.authorization_id, self.manager.user_id)
        
        self.assertIsNotNone(rejected)
        self.assertEqual(rejected.authorization_status, 'Rejected')

    def test_delete_proposal(self):
        proposal = propose_asset("Misc", self.proposer.user_id)
        success = delete_proposal(proposal.authorization_id)
        self.assertTrue(success)
        self.assertIsNone(AssetAuthorization.query.get(proposal.authorization_id))
