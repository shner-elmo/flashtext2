import unittest
import json

from flashtext_cy import KeywordProcessor


class TestKeywordExtractor(unittest.TestCase):
    def setUp(self):
        with open('keyword_extractor_test_cases.json') as f:
            self.test_cases = json.load(f)

    def test_extract_keywords(self):
        """
        For each of the test case initialize a new KeywordProcessor.
        Add the keywords the test case to KeywordProcessor.
        Extract keywords and check if they match the expected result for the test case.
        """
        for test_id, test_case in enumerate(self.test_cases):
            kp = KeywordProcessor()
            kp.add_keywords(test_case['keyword_dict'])
            keywords_extracted = kp.extract_keywords(test_case['sentence'], span_info=False)
            self.assertEqual(test_case['keywords'], keywords_extracted, (test_id, test_case))

    def test_extract_keywords_case_sensitive(self):
        """
        For each of the test case initialize a new KeywordProcessor.
        Add the keywords the test case to KeywordProcessor.
        Extract keywords and check if they match the expected result for the test case.
        """
        for test_id, test_case in enumerate(self.test_cases):
            kp = KeywordProcessor(case_sensitive=True)
            kp.add_keywords(test_case['keyword_dict'])
            keywords_extracted = kp.extract_keywords(test_case['sentence'], span_info=False)
            self.assertEqual(test_case['keywords_case_sensitive'], keywords_extracted, (test_id, test_case))

# TODO: add tests that run the JSON test-cases with span_info=True,
#  and simply check if `og_string[span_info_x:span_info_y] == extracted_keyword`
