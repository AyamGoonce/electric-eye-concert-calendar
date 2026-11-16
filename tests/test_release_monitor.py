"""Phase 4 monitoring is advisory and preserves existing publication gates."""
import unittest

from concert_calendar.release_monitor import build_monitoring_report, markdown_summary


def example_report():
    return {
        "published_at": "2026-11-16T16:30:00Z",
        "event_count": 2113,
        "genre_report": {"total": 2113, "populated": 1294, "blank": 819,
                         "coverage_percentage": 61.92, "conflict_count": 9},
        "genre_acceptance": {
            "baseline_comparable_ids": 2105,
            "blank_reasons": {"blank_no_raw": 742, "blank_unresolved_raw": 60,
                              "blank_festival": 6, "blank_unresolved_taxonomy": 2,
                              "conflict_count": 9},
            "genre_losses_on_retained_ids": [{"id": "a", "artist": "Deca Joins"}],
            "billing_changes_on_retained_ids": [{"id": "b", "before": [], "after": []}],
            "provenance_defects": [],
            "candidate_only_ids": 8, "baseline_only_ids": 0,
        },
        "reconciliation_quality": {
            "possible_flat_bill": {"count": 78},
            "possible_programme_as_artist": {"count": 35},
        },
    }


class ReleaseMonitorTests(unittest.TestCase):
    def test_known_phase3_release_is_review_not_alarm(self):
        result = build_monitoring_report(example_report())
        self.assertEqual("review", result["status"])
        self.assertEqual(["genre_loss", "billing_churn"],
                         [item["code"] for item in result["alerts"]])
        self.assertEqual(819, result["metrics"]["genre_blank"])
        self.assertIn("advisory", markdown_summary(result))

    def test_no_baseline_is_not_misreported_as_missing_events(self):
        source = example_report()
        source["genre_acceptance"].update(
            baseline_comparable_ids=0, baseline_only_ids=0,
            genre_losses_on_retained_ids=[], billing_changes_on_retained_ids=[])
        result = build_monitoring_report(source)
        self.assertEqual("normal", result["status"])

    def test_high_billing_churn_is_investigate_not_a_publication_gate(self):
        source = example_report()
        source["genre_acceptance"]["billing_changes_on_retained_ids"] = [
            {"id": str(i)} for i in range(50)
        ]
        result = build_monitoring_report(source)
        self.assertEqual("investigate", result["status"])
        self.assertEqual(50, result["metrics"]["billing_change_examples"])
        self.assertLessEqual(len(result["examples"]["billing_changes"]), 20)

    def test_missing_provenance_requires_investigation(self):
        source = example_report()
        source["genre_acceptance"]["provenance_defects"] = [{"artist": "A"}]
        result = build_monitoring_report(source)
        self.assertEqual("investigate", result["status"])
        self.assertIn("genre_provenance", [a["code"] for a in result["alerts"]])

    def test_review_queue_thresholds_are_advisory(self):
        source = example_report()
        source["reconciliation_quality"]["possible_flat_bill"]["count"] = 105
        source["reconciliation_quality"]["possible_programme_as_artist"]["count"] = 55
        result = build_monitoring_report(source)
        self.assertIn("flat_bill_review_queue", [a["code"] for a in result["alerts"]])
        self.assertIn("programme_title_review_queue", [a["code"] for a in result["alerts"]])


if __name__ == "__main__":
    unittest.main()
