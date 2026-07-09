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


@allure.epic("ADO Shop Business Logic")
@allure.feature("Cart Flow")
class TestCartFlow:

    @allure.story("Empty cart message")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_cart_empty_message(self, driver):
        page = open_page(driver, "cart")
        assert page.cart_empty_message.is_visible()

    @allure.story("Cart page URL")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_cart_url(self, driver):
        open_page(driver, "cart")
        assert "/cart" in driver.current_url

    @allure.story("Checkout button present on empty cart")
    @allure.severity(allure.severity_level.NORMAL)
    def test_checkout_on_empty_cart(self, driver):
        page = open_page(driver, "cart")
        assert page.checkout_button.is_visible()

    @allure.story("Cart icon in header")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_cart_icon_in_header(self, driver):
        page = open_page(driver)
        assert page.cart_link.is_visible()


@allure.epic("ADO Shop Business Logic")
@allure.feature("Product Selection")
class TestProductSelection:

    def _get_first_product_url(self, driver):
        page = open_page(driver, "collections/all")
        assert page.product_title_links.count() > 0
        return page.product_title_links[0].get_attribute("href")

    @allure.story("Product has add to cart button")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_add_to_cart_button(self, driver):
        href = self._get_first_product_url(driver)
        driver.get(href)
        time.sleep(3)
        page = MainPage(driver)
        assert page.product_add_to_cart.is_visible()

    @allure.story("Product has price")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_product_has_price(self, driver):
        href = self._get_first_product_url(driver)
        driver.get(href)
        time.sleep(3)
        page = MainPage(driver)
        assert page.product_price.is_visible()

    @allure.story("Product has title")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_product_has_title(self, driver):
        href = self._get_first_product_url(driver)
        driver.get(href)
        time.sleep(3)
        page = MainPage(driver)
        title = page.product_title.get_text()
        assert title and title.strip()

    @allure.story("Product has description")
    @allure.severity(allure.severity_level.NORMAL)
    def test_product_has_description(self, driver):
        href = self._get_first_product_url(driver)
        driver.get(href)
        time.sleep(3)
        page = MainPage(driver)
        assert page.product_description.is_visible()

    @allure.story("Product has image")
    @allure.severity(allure.severity_level.NORMAL)
    def test_product_has_image(self, driver):
        href = self._get_first_product_url(driver)
        driver.get(href)
        time.sleep(3)
        page = MainPage(driver)
        assert page.product_image.is_visible()

    @allure.story("Product image has src")
    @allure.severity(allure.severity_level.MINOR)
    def test_product_image_has_src(self, driver):
        href = self._get_first_product_url(driver)
        driver.get(href)
        time.sleep(3)
        page = MainPage(driver)
        src = page.product_image.get_attribute("src")
        assert src and src.startswith("http")


@allure.epic("ADO Shop Business Logic")
@allure.feature("Search Flow")
class TestSearchFlow:

    @allure.story("Search finds products")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_returns_results(self, driver):
        page = open_page(driver)
        page.search_toggle.click()
        page.search_input.send_keys("Zanmu")
        time.sleep(3)
        assert page.search_results.is_visible()

    @allure.story("Search with no results")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_no_results(self, driver):
        page = open_page(driver)
        page.search_toggle.click()
        page.search_input.send_keys("zzzznonexistent12345")
        time.sleep(3)
        results = driver.find_elements(
            By.XPATH, "//*[contains(text(),'No results')]"
        )
        assert len(results) > 0
