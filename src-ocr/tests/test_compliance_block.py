import unittest
from rules import evaluate_compliance, evaluate_validation_rules

class TestComplianceBlock(unittest.TestCase):
    def test_compliance_blocked_when_validation_fails(self):
        text = "Contact: test@example.com"
        # create a validation result list that simulates a FAIL overall
        val_res = [
            {"id": "VAL-001", "status": "FAIL"},
            {"id": "VAL-002", "status": "PASS"},
        ]
        comp_res = evaluate_compliance(text, validation_results=val_res)
        # all compliance results should be BLOCKED
        self.assertTrue(all(r['status'] == 'BLOCKED' for r in comp_res))

if __name__ == '__main__':
    unittest.main()
