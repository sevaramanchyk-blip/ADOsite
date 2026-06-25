import pytest
from helpers.utils import find_typos, COMMON_TYPOS


class TestFindTypos:
    def test_finds_known_typo(self):
        texts = ["This is teh test"]
        result = find_typos(texts)
        assert len(result) == 1
        assert result[0][0] == "teh"
        assert result[0][1] == "the"

    def test_no_typos(self):
        texts = ["This text is correct"]
        result = find_typos(texts)
        assert result == []

    def test_multiple_typos(self):
        texts = ["taht teh recieve"]
        result = find_typos(texts)
        assert len(result) == 3

    def test_case_insensitive(self):
        texts = ["This is TEH test"]
        result = find_typos(texts)
        assert len(result) == 1
        assert result[0][0] == "teh"

    def test_ignores_non_english(self):
        texts = ["Это русский текст"]
        result = find_typos(texts)
        assert result == []

    def test_empty_input(self):
        result = find_typos([])
        assert result == []

    def test_returns_context(self):
        texts = ["a" * 50 + " teh " + "b" * 20]
        result = find_typos(texts)
        assert len(result[0][2]) == 60

    def test_multiple_texts(self):
        texts = ["teh first", "recieve second"]
        result = find_typos(texts)
        assert len(result) == 2

    def test_no_match_partial(self):
        texts = ["technology"]
        result = find_typos(texts)
        assert result == []

    def test_word_boundaries(self):
        texts = ["tehre"]
        result = find_typos(texts)
        assert result == []


class TestCommonTypos:
    def test_typo_dict_not_empty(self):
        assert len(COMMON_TYPOS) > 0

    def test_all_values_are_strings(self):
        for key, value in COMMON_TYPOS.items():
            assert isinstance(key, str)
            assert isinstance(value, str)
