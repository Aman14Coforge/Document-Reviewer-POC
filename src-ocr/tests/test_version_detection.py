import unittest

from rules import detect_document_version


class TestVersionDetection(unittest.TestCase):
    def test_version_in_text_v_prefixed(self):
        self.assertEqual(detect_document_version("Version: v1.2"), "v1.2")

    def test_version_in_text_unprefixed(self):
        self.assertEqual(detect_document_version("version 2.3"), "v2.3")

    def test_rev_in_text(self):
        self.assertEqual(detect_document_version("Rev. 3.0"), "v3.0")

    def test_in_filename(self):
        self.assertEqual(detect_document_version("", "mydoc_v4.5.docx"), "v4.5")

    def test_no_version(self):
        self.assertEqual(detect_document_version("no version here", ""), "")


if __name__ == '__main__':
    unittest.main()
