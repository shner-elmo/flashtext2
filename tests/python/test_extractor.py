import unittest
import json
import logging

from flashtext2 import KeywordProcessor

logger = logging.getLogger(__name__)


class TestKeywordExtractor(unittest.TestCase):
    def setUp(self):
        logger.info("Starting...")
        with open('keyword_extractor_test_cases.json') as f:
            self.test_cases = json.load(f)

    def tearDown(self):
        logger.info("Ending.")

    def test_extract_keywords(self):
        """
        For each of the test case initialize a new KeywordProcessor.
        Add the keywords the test case to KeywordProcessor.
        Extract keywords and check if they match the expected result for the test case.
        """
        for test_id, test_case in enumerate(self.test_cases):
            kp = KeywordProcessor()
            kp.add_keywords_with_clean_word(
                [(val, key) for key, values in test_case['keyword_dict'].items() for val in
                 values]
            )
            keywords_extracted = kp.extract_keywords(test_case['sentence'])
            self.assertEqual(test_case['keywords'], keywords_extracted, (test_id, test_case))

    def test_extract_keywords_case_sensitive(self):
        """
        For each of the test case initialize a new KeywordProcessor.
        Add the keywords the test case to KeywordProcessor.
        Extract keywords and check if they match the expected result for the test case.
        """
        for test_id, test_case in enumerate(self.test_cases):
            kp = KeywordProcessor(case_sensitive=True)
            kp.add_keywords_from_dict(test_case['keyword_dict'])
            keywords_extracted = kp.extract_keywords(test_case['sentence'], span_info=False)
            self.assertEqual(test_case['keywords_case_sensitive'], keywords_extracted, (test_id, test_case))
