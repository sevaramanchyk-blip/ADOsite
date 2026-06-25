import pytest
from helpers.config import BASE_URL, MAIN_URL, COLLECTIONS


class TestConfig:
    def test_base_url_not_empty(self):
        assert BASE_URL is not None
        assert len(BASE_URL) > 0

    def test_main_url_not_empty(self):
        assert MAIN_URL is not None
        assert len(MAIN_URL) > 0

    def test_base_url_is_string(self):
        assert isinstance(BASE_URL, str)

    def test_main_url_is_string(self):
        assert isinstance(MAIN_URL, str)

    def test_collections_is_list(self):
        assert isinstance(COLLECTIONS, list)

    def test_collections_not_empty(self):
        assert len(COLLECTIONS) > 0

    def test_collections_have_tuples(self):
        for item in COLLECTIONS:
            assert isinstance(item, tuple)
            assert len(item) == 2

    def test_collection_slugs_are_strings(self):
        for slug, name in COLLECTIONS:
            assert isinstance(slug, str)
            assert isinstance(name, str)

    def test_collection_slugs_not_empty(self):
        for slug, name in COLLECTIONS:
            assert len(slug) > 0
            assert len(name) > 0
