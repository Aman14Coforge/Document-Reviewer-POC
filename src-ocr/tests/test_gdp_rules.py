import unittest
from pathlib import Path
import importlib.util

spec = importlib.util.spec_from_file_location("rules_mod", str(Path(__file__).parents[1] / 'rules.py'))
rules = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rules)

class TestGDPRules(unittest.TestCase):
    def test_gdp_rules_not_forced_pass_when_validation_fails(self):
        # Create a document text that will cause validation to fail (missing title and version)
        text = (
            "\n"  # empty first line -> no title
            "This document contains lorem ipsum and teh mistakes.\n"
            "No version here.\n"
            "Signature: none\n"
        )

        # Run validation results which should contain FAIL entries
        val_res = rules.evaluate_validation_rules(text, document_title="", version="", metadata={})
        # Ensure at least one VAL rule failed
        self.assertTrue(any(r['status'] == 'FAIL' for r in val_res), "Expected at least one VAL rule to fail")

        # Now run GDP rules with the failing validation results provided
        gdp_res = rules.evaluate_document_rules(text, validation_results=val_res)

        # When validation failed, GDP rules should be BLOCKED to avoid misleading PASS/FAIL
        self.assertTrue(all(r['status'] == 'BLOCKED' for r in gdp_res), "Expected GDP rules to be BLOCKED when validation failed")

if __name__ == '__main__':
    unittest.main()
