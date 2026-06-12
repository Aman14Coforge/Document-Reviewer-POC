import unittest
from pathlib import Path
import importlib.util

spec = importlib.util.spec_from_file_location("rules_mod", str(Path(__file__).parents[1] / 'rules.py'))
rules = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rules)

class TestRules(unittest.TestCase):
    def test_evaluate_validation_rules_empty(self):
        res = rules.evaluate_validation_rules("")
        # VAL-001 should fail when title is blank
        val1 = next(r for r in res if r['id'] == 'VAL-001')
        self.assertEqual(val1['status'], 'FAIL')

    def test_evaluate_validation_rules_good(self):
        text = (
            "Document Title\n"
            "v1.0\n"
            "Revision History\n"
            "2024-01-01: initial\n"
            "Signature: Approved by Alice\n"
        )
        res = rules.evaluate_validation_rules(text, document_title='Document Title', version='v1.0', metadata={'has_audit_trail': True}, file_name='doc.pdf')
        # VAL-001 and VAL-002 should pass
        val1 = next(r for r in res if r['id'] == 'VAL-001')
        val2 = next(r for r in res if r['id'] == 'VAL-002')
        self.assertEqual(val1['status'], 'PASS')
        self.assertEqual(val2['status'], 'PASS')

    def test_evaluate_compliance_sensitive(self):
        text = "Contact: test@example.com"
        res = rules.evaluate_compliance(text)
        cmp1 = next(r for r in res if r['id'] == 'CMP-01')
        self.assertEqual(cmp1['status'], 'FAIL')

    def test_evaluate_document_rules_language(self):
        text = "Document Title\nThis text has teh error and lorem ipsum and  (unbalanced"
        res = rules.evaluate_document_rules(text)
        gdp9 = next(r for r in res if r['id'] == 'GDP-09')
        self.assertEqual(gdp9['status'], 'FAIL')

if __name__ == '__main__':
    unittest.main()
