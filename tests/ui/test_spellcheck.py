import time
import pytest
import allure
from selenium.webdriver.common.by import By
from helpers.config import BASE_URL
from core.locators.main_locators import MainPage


def open_page(driver, path=""):
    url = f"{BASE_URL}/{path}" if path else BASE_URL
    page = MainPage(driver, url)
    return page


KNOWN_WORDS = [
    "Ado", "Hibana", "Zanmu", "Shinzou", "Phantom Siita",
    "Yodaka", "Vivarium", "Merch", "Cart", "Checkout", "Search", "Music",
    "Privacy Policy", "Refund Policy", "Terms of Service",
]


@allure.epic("ADO Shop Spellcheck")
@allure.feature("Page Text Validation")
class TestHomepageSpellcheck:

    @allure.story("Homepage title contains Ado")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_homepage_title(self, driver):
        open_page(driver)
        title = driver.title
        assert "Ado" in title or "ado" in title.lower()

    @allure.story("Homepage has main content")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_homepage_main_content(self, driver):
        page = open_page(driver)
        assert page.main_content.is_visible()

    @allure.story("Homepage h1 is not empty")
    @allure.severity(allure.severity_level.NORMAL)
    def test_homepage_h1_not_empty(self, driver):
        page = open_page(driver)
        page.scroll_down()
        assert page.h1_title.is_visible()


@allure.epic("ADO Shop Spellcheck")
@allure.feature("Page Text Validation")
class TestCollectionSpellcheck:

    @allure.story("Collection page has non-empty h1")
    @allure.severity(allure.severity_level.NORMAL)
    def test_collection_h1(self, driver):
        page = open_page(driver, "collections/all")
        h1_text = page.h1_title.get_text()
        assert h1_text and h1_text.strip()

    @allure.story("Product titles are not empty")
    @allure.severity(allure.severity_level.NORMAL)
    def test_product_titles_not_empty(self, driver):
        page = open_page(driver, "collections/all")
        count = page.product_title_links.count()
        assert count > 0
        for i in range(min(count, 5)):
            href = page.product_title_links[i].get_attribute("href")
            assert href and "/products/" in href


@allure.epic("ADO Shop Spellcheck")
@allure.feature("Page Text Validation")
class TestProductSpellcheck:

    def _open_first_product(self, driver):
        page = open_page(driver, "collections/all")
        assert page.product_title_links.count() > 0
        href = page.product_title_links[0].get_attribute("href")
        driver.get(href)
        time.sleep(3)

    @allure.story("Product title not empty")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_product_title_not_empty(self, driver):
        self._open_first_product(driver)
        page = MainPage(driver)
        title = page.product_title.get_text()
        assert title and title.strip()

    @allure.story("Product title matches known words")
    @allure.severity(allure.severity_level.NORMAL)
    def test_product_title_known_words(self, driver):
        self._open_first_product(driver)
        page = MainPage(driver)
        title = page.product_title.get_text()
        has_known = any(w.lower() in title.lower() for w in KNOWN_WORDS)
        assert has_known


@allure.epic("ADO Shop Spellcheck")
@allure.feature("Page Text Validation")
class TestPolicySpellcheck:

    @pytest.mark.parametrize("policy_path,expected_text", [
        ("policies/privacy-policy", "Privacy"),
        ("policies/refund-policy", "Refund"),
        ("policies/terms-of-service", "Terms"),
    ])
    @allure.story("Policy page loads with correct text")
    @allure.severity(allure.severity_level.NORMAL)
    def test_policy_page_text(self, driver, policy_path, expected_text):
        open_page(driver, policy_path)
        body = driver.find_element(By.TAG_NAME, "body").text
        assert expected_text.lower() in body.lower()
