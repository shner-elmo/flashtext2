import unittest
import json
import logging

from flashtext2 import KeywordProcessor

logger = logging.getLogger(__name__)


class TestKeywordExtractor(unittest.TestCase):
    def setUp(self):
        logger.info("Starting...")
        with open('tests/keyword_extractor_test_cases.json') as f:
            self.test_cases = json.load(f)

    def tearDown(self):
        logger.info("Ending.")

    def test_extract_keywords(self):
        for test_id, test_case in enumerate(self.test_cases):
            kp = KeywordProcessor(case_sensitive=False)
            kp.add_keywords_with_clean_word_from_iter(
                (val, key) for key, values in test_case['keyword_dict'].items() for val in values
            )
            keywords_extracted = kp.extract_keywords(test_case['sentence'])
            self.assertEqual(test_case['keywords'], keywords_extracted, (test_id, test_case))

    def test_extract_keywords_case_sensitive(self):
        for test_id, test_case in enumerate(self.test_cases):
            kp = KeywordProcessor(case_sensitive=True)
            kp.add_keywords_with_clean_word_from_iter(
                (val, key) for key, values in test_case['keyword_dict'].items() for val in values
            )
            keywords_extracted = kp.extract_keywords(test_case['sentence'])
            self.assertEqual(test_case['keywords_case_sensitive'], keywords_extracted, (test_id, test_case))

    def test_keywords_span(self):
        for test_id, test_case in enumerate(self.test_cases):
            kp = KeywordProcessor(case_sensitive=True)
            kp.add_keywords_from_iter(
                val for _, values in test_case['keyword_dict'].items() for val in values
            )
            text = test_case['sentence']
            for (kw, start, end) in kp.extract_keywords_with_span(text):
                self.assertEqual(text[start:end], kw)
                