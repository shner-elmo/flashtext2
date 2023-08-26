from __future__ import annotations

import json

from flashtext2 import KeywordProcessor


# tests copied from:
with open('keyword_extractor_test_cases.json', 'r', encoding='utf-8') as f:
    TEST_CASES = json.load(f)


def test_extract_keywords():
    """
    Test `extract_keywords` with `case_sensitive=False`
    """
    for test_id, test_case in enumerate(TEST_CASES):
        kp = KeywordProcessor(case_sensitive=False)
        kp.add_keywords_from_dict(test_case['keyword_dict'])

        keywords_extracted = kp.extract_keywords(test_case['sentence'], span_info=False)
        assert keywords_extracted == test_case['keywords'], (test_id, test_case)


def test_extract_keywords_case_sensitive():
    """
    Test `extract_keywords` with `case_sensitive=True`
    """
    for test_id, test_case in enumerate(TEST_CASES):
        kp = KeywordProcessor(case_sensitive=True)
        kp.add_keywords_from_dict(test_case['keyword_dict'])

        keywords_extracted = kp.extract_keywords(test_case['sentence'], span_info=False)
        assert keywords_extracted == test_case['keywords_case_sensitive'], (test_id, test_case)


def test_extract_keywords_with_span():
    """
    Test `extract_keywords` with `span_info=True`
    """
    for test_id, test_case in enumerate(TEST_CASES):
        kp = KeywordProcessor(case_sensitive=False)
        kp.add_keywords_from_dict(test_case['keyword_dict'])
        sentence = test_case['sentence']

        for word, start, end in kp.extract_keywords(sentence, span_info=True):
            # TODO: check if `assert word == sentence[start:end].lower()` is necessary.
            assert word == sentence[start:end], (test_id, test_case)


def test_extract_keywords_with_span_case_sensitive():
    """
    Test `extract_keywords` with `span_info=True`
    """
    for test_id, test_case in enumerate(TEST_CASES):
        kp = KeywordProcessor(case_sensitive=True)
        kp.add_keywords_from_dict(test_case['keyword_dict'])
        sentence = test_case['sentence']

        for word, start, end in kp.extract_keywords(sentence, span_info=True):
            # TODO: check if `assert word == sentence[start:end].lower()` is necessary.
            assert word == sentence[start:end], (test_id, test_case)


def test_replace_keywords():
    """
    Test `replace_keywords` with `case_sensitive=False`
    """
    for test_id, test_case in enumerate(TEST_CASES):
        kp = KeywordProcessor(case_sensitive=False)
        kp.add_keywords_from_dict(test_case['keyword_dict'])
        sentence = test_case['sentence']

        new_sentence = kp.replace_keywords(sentence)

        s = sentence.copy()
        for word, clean_word in kp.get_keywords():
            s = s.replace(word, clean_word)

        assert new_sentence == s, (test_id, test_case)


def test_replace_keywords_case_sensitive():
    """
    Test `replace_keywords` with `case_sensitive=True`
    """
    for test_id, test_case in enumerate(TEST_CASES):
        kp = KeywordProcessor(case_sensitive=True)
        kp.add_keywords_from_dict(test_case['keyword_dict'])
        sentence = test_case['sentence']

        new_sentence = kp.replace_keywords(sentence)

        s = sentence.copy()
        for word, clean_word in kp.get_keywords():
            s = s.replace(word, clean_word)

        assert new_sentence == s, (test_id, test_case)
