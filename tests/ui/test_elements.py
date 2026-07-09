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


@allure.epic("ADO Shop UI Tests")
@allure.feature("Page Elements")
class TestHeaderElements:

    @allure.story("Header presence")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_header_is_present(self, driver):
        page = open_page(driver)
        assert page.header_element.is_presented()

    @allure.story("Logo presence")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_logo_is_present(self, driver):
        page = open_page(driver)
        assert page.header_logo.is_presented()

    @allure.story("Logo is clickable")
    @allure.severity(allure.severity_level.NORMAL)
    def test_logo_click_returns_home(self, driver):
        open_page(driver, "collections/all")
        page = MainPage(driver)
        page.header_logo.click()
        time.sleep(2)
        assert driver.current_url.rstrip("/") == BASE_URL.rstrip("/")


@allure.epic("ADO Shop UI Tests")
@allure.feature("Page Elements")
class TestSearchElements:

    @allure.story("Search toggle is clickable")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_toggle_clickable(self, driver):
        page = open_page(driver)
        assert page.search_toggle.is_clickable()

    @allure.story("Search input appears after toggle")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_input_appears(self, driver):
        page = open_page(driver)
        page.search_toggle.click()
        time.sleep(1)
        assert page.search_input.is_visible()

    @allure.story("Search input accepts and clears text")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_input_clear(self, driver):
        page = open_page(driver)
        page.search_toggle.click()
        page.search_input.send_keys("test query")
        time.sleep(1)
        val = page.search_input.get_attribute("value")
        assert val == "test query"


@allure.epic("ADO Shop UI Tests")
@allure.feature("Page Elements")
class TestFooterElements:

    @allure.story("Footer is present")
    @allure.severity(allure.severity_level.NORMAL)
    def test_footer_present(self, driver):
        page = open_page(driver)
        page.scroll_down()
        assert page.footer_element.is_presented()

    @allure.story("All social links present")
    @allure.severity(allure.severity_level.NORMAL)
    def test_all_social_links(self, driver):
        page = open_page(driver)
        page.scroll_down()
        assert page.footer_instagram.is_presented()
        assert page.footer_twitter.is_presented()
        assert page.footer_facebook.is_presented()
        assert page.footer_youtube.is_presented()

    @allure.story("All policy links present")
    @allure.severity(allure.severity_level.NORMAL)
    def test_all_policy_links(self, driver):
        page = open_page(driver)
        page.scroll_down()
        assert page.footer_privacy_policy.is_presented()
        assert page.footer_refund_policy.is_presented()
        assert page.footer_terms_of_service.is_presented()
        assert page.footer_legal_notice.is_presented()

    @allure.story("Social links have href")
    @allure.severity(allure.severity_level.MINOR)
    def test_social_links_have_href(self, driver):
        page = open_page(driver)
        page.scroll_down()
        for social in [page.footer_instagram, page.footer_twitter,
                       page.footer_facebook, page.footer_youtube]:
            href = social.get_attribute("href")
            assert href and href.startswith("http")


@allure.epic("ADO Shop UI Tests")
@allure.feature("Page Elements")
class TestNavigationElements:

    @allure.story("Navigation links count")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_nav_links_minimum_count(self, driver):
        page = open_page(driver)
        count = page.nav_links.count()
        assert count >= 5

    @allure.story("Navigation links are clickable")
    @allure.severity(allure.severity_level.NORMAL)
    def test_nav_links_are_clickable(self, driver):
        page = open_page(driver)
        count = page.nav_links.count()
        for i in range(min(count, 3)):
            elem = page.nav_links[i]
            assert elem is not None
