"""Unit-тесты конфигурации нагрузочного тестирования."""

import pytest
from helpers.load_config import PAGES
from helpers.config import MAIN_URL


class TestLoadConfig:
    def test_pages_is_list(self):
        assert isinstance(PAGES, list)

    def test_pages_not_empty(self):
        assert len(PAGES) > 0

    def test_first_page_is_main_url(self):
        assert PAGES[0] == MAIN_URL

    def test_all_pages_are_strings(self):
        for page in PAGES:
            assert isinstance(page, str)

    def test_all_pages_start_with_main_url(self):
        for page in PAGES:
            assert page.startswith(MAIN_URL)

    def test_pages_contain_collections(self):
        collections = [p for p in PAGES if "collections/" in p]
        assert len(collections) > 0
