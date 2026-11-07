"""Safety tests for explicit waiver approval and the demo audit ledger."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from ta2.human_approval import request_human_approval
from ta2.waiver_store import WaiverStore


class HumanApprovalTests(unittest.TestCase):
    def test_exact_request_phrase_approves(self):
        with patch("builtins.input", return_value="APPROVE req-123"):
            result = request_human_approval(
                "M001", "10", "exceptional circumstances", "req-123"
            )
        self.assertTrue(result["approved"])
        self.assertEqual(result["status"], "APPROVED")
        self.assertFalse(result["authenticated_identity"])

    def test_plain_yes_does_not_approve(self):
        with patch("builtins.input", return_value="yes"):
            result = request_human_approval(
                "M001", "10", "exceptional circumstances", "req-123"
            )
        self.assertFalse(result["approved"])
        self.assertEqual(result["status"], "DENIED")

    def test_wrong_request_id_does_not_approve(self):
        with patch("builtins.input", return_value="APPROVE req-other"):
            result = request_human_approval(
                "M001", "10", "exceptional circumstances", "req-123"
            )
        self.assertFalse(result["approved"])


class WaiverLedgerTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test.db"
        self.store = WaiverStore(self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_only_matching_approval_can_be_recorded(self):
        with self.assertRaises(PermissionError):
            self.store.record_approved_waiver(
                request_id="req-123",
                member_id="M001",
                fine_amount="10",
                reason="exceptional circumstances",
                approval={
                    "request_id": "req-123",
                    "approved": False,
                    "status": "DENIED",
                },
            )
        self.assertIsNone(self.store.get_event("req-123"))

    def test_approved_event_is_audited_and_cannot_be_replayed(self):
        approval = {
            "request_id": "req-123",
            "approved": True,
            "status": "APPROVED",
            "approval_method": "exact_interactive_confirmation",
            "authenticated_identity": False,
        }
        result = self.store.record_approved_waiver(
            request_id="req-123",
            member_id="M001",
            fine_amount="10",
            reason="exceptional circumstances",
            approval=approval,
        )
        self.assertEqual(result["status"], "APPROVED")
        event = self.store.get_event("req-123")
        self.assertEqual(event["member_id"], "M001")
        self.assertEqual(event["fine_amount"], "10")
        self.assertEqual(event["status"], "APPROVED")
        self.assertEqual(event["authenticated_identity"], 0)

        with self.assertRaises(Exception):
            self.store.record_approved_waiver(
                request_id="req-123",
                member_id="M001",
                fine_amount="10",
                reason="exceptional circumstances",
                approval=approval,
            )


if __name__ == "__main__":
    unittest.main()
