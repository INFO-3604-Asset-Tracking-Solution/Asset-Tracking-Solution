import unittest
from App.models import Audit, CheckEvent
from App.controllers.audit import (
    create_audit, end_audit, get_all_audits, get_audit_by_id,
    get_audit_status, generate_interim_report, generate_final_report,
    get_active_audit
)
from App.database import db

class AuditCRUDIntegrationTests(unittest.TestCase):
    def setUp(self):
        # Clean up audits before each test
        for audit in Audit.query.all():
            db.session.delete(audit)
        db.session.commit()

    def test_create_and_get_audit(self):
        # Act
        new_audit = create_audit(initiator_id=1)
        
        # Assert
        self.assertIsNotNone(new_audit)
        self.assertIsNotNone(new_audit.audit_id)
        self.assertEqual(new_audit.status, "IN_PROGRESS")
        self.assertEqual(new_audit.initiator_id, 1)

        retrieved_audit = get_audit_by_id(new_audit.audit_id)
        self.assertIsNotNone(retrieved_audit)
        self.assertEqual(retrieved_audit.status, "IN_PROGRESS")
        
        # Test status JSON
        status = get_audit_status()
        self.assertEqual(status, "IN_PROGRESS")

    def test_singleton_active_audit(self):
        audit1 = create_audit(initiator_id=1)
        audit2 = create_audit(initiator_id=2)
        
        # It should return the same active audit instance rather than making a new one
        self.assertEqual(audit1.audit_id, audit2.audit_id)
        self.assertEqual(audit2.initiator_id, 1)

    def test_end_audit(self):
        audit = create_audit(initiator_id=1)
        active = get_active_audit()
        self.assertEqual(active.audit_id, audit.audit_id)

        # End audit
        ended_audit = end_audit()
        self.assertIsNotNone(ended_audit)
        self.assertEqual(ended_audit.status, "COMPLETED")
        self.assertIsNotNone(ended_audit.end_date)
        
        status = get_audit_status()
        self.assertEqual(status, "NO_ACTIVE_AUDIT")

    def test_reports(self):
        audit = create_audit(initiator_id=1)
        
        interim = generate_interim_report(audit.audit_id)
        self.assertIsNotNone(interim)
        self.assertIn('found_correct', interim)
        self.assertIn('relocated', interim)
        self.assertIn('missing', interim)
        self.assertIn('condition_discrepancy', interim)
        
        end_audit()
        
        # Now interim should be None because it's COMPLETED
        interim_after = generate_interim_report(audit.audit_id)
        self.assertIsNone(interim_after)
        
        # Final report
        final = generate_final_report(audit.audit_id)
        self.assertIsNotNone(final)
        self.assertIn('missing', final)
        self.assertIn('found_correct', final)

