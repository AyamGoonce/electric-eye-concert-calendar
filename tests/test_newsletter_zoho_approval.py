"""Regression tests for Zoho newsletter approval orchestration."""

import unittest

from newsletter.zoho_approval import process_approval
from newsletter.zoho_campaigns import campaign_name, campaign_editor_url


class ApprovalOrchestrationTests(unittest.TestCase):
    frequency = "weekly"
    identifier = "2026-W42"

    def setUp(self):
        campaign_id = "221575000000113002"
        self.campaign = {
            "frequency": self.frequency,
            "identifier": self.identifier,
            "campaign_name": campaign_name(self.frequency, self.identifier),
            "campaign_id": campaign_id,
            "campaign_status": "Draft",
            "editor_url": campaign_editor_url(campaign_id),
        }
        self.events = []
        self.exists_calls = 0

    def execute(self, *, existing=False, smtp_failure=False,
                record_failure=False, appears_later=False):
        def verify(frequency, identifier, **kwargs):
            self.events.append("verify")
            self.assertEqual(frequency, self.frequency)
            self.assertEqual(identifier, self.identifier)
            return True

        def exists(frequency, identifier, **kwargs):
            self.exists_calls += 1
            self.events.append("exists")
            return existing or (appears_later and self.exists_calls == 2)

        def prepare(frequency, identifier, **kwargs):
            self.events.append("prepare")
            return self.campaign

        def notify(campaign):
            self.events.append("notify")
            if smtp_failure:
                raise RuntimeError("Simulated SMTP failure")
            return {"recipient": "eric@electriceyerock.com"}

        def record(campaign, **kwargs):
            self.events.append("record")
            if record_failure:
                raise RuntimeError("Simulated GitHub write failure")
            return {
                "action": "created",
                "path": "approvals/weekly/2026-W42.json",
            }

        return process_approval(
            self.frequency,
            self.identifier,
            publish_token="TEST_TOKEN",
            prepare_func=prepare,
            notify_func=notify,
            exists_func=exists,
            verify_func=verify,
            record_func=record,
        )

    def test_existing_notification_skips_processing(self):
        result = self.execute(existing=True)
        self.assertEqual(result["action"], "already_notified")
        self.assertEqual(self.events, ["verify", "exists"])

    def test_new_approval_notifies_and_records(self):
        result = self.execute()
        self.assertEqual(result["action"], "notified")
        self.assertEqual(
            self.events,
            ["verify", "exists", "prepare", "exists", "notify", "record"],
        )

    def test_smtp_failure_does_not_record(self):
        with self.assertRaisesRegex(RuntimeError, "SMTP failure"):
            self.execute(smtp_failure=True)
        self.assertNotIn("record", self.events)

    def test_record_failure_reports_partial_delivery(self):
        with self.assertRaisesRegex(RuntimeError, "could not be saved"):
            self.execute(record_failure=True)
        self.assertEqual(self.events[-2:], ["notify", "record"])

    def test_late_duplicate_detection_prevents_delivery(self):
        result = self.execute(appears_later=True)
        self.assertEqual(result["action"], "already_notified")
        self.assertNotIn("notify", self.events)
        self.assertNotIn("record", self.events)


if __name__ == "__main__":
    unittest.main()
