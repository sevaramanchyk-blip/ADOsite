import time
import pytest
import allure
from selenium.webdriver.common.by import By
from helpers.config import BASE_URL, COLLECTIONS
from core.locators.main_locators import MainPage


def open_page(driver, path=""):
    url = f"{BASE_URL}/{path}" if path else BASE_URL
    page = MainPage(driver, url)
    return page


@allure.epic("ADO Shop")
@allure.feature("Collections")
class TestCollections:

    @allure.story("ALL MUSIC collection loads")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_all_music(self, driver):
        page = open_page(driver, "collections/all")
        assert page.collection_product_grid.is_visible()

    @allure.story("Collection has product items")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_collection_has_products(self, driver):
        page = open_page(driver, "collections/all")
        assert page.collection_product_items.count() > 0

    @pytest.mark.parametrize("slug", [
        "hibana",
        "2nd-original-album-zanmu",
        "phantom-siita",
        "all-merch",
        "shinzou",
        "ados-best-adobum",
    ])
    @allure.story("Collection loads by slug")
    @allure.severity(allure.severity_level.NORMAL)
    def test_collection_by_slug(self, driver, slug):
        page = open_page(driver, f"collections/{slug}")
        assert page.collection_product_grid.is_visible()


@allure.epic("ADO Shop")
@allure.feature("Product Pages")
class TestProductPages:

    def _open_first_product(self, driver):
        page = open_page(driver, "collections/all")
        assert page.product_title_links.count() > 0
        href = page.product_title_links[0].get_attribute("href")
        driver.get(href)
        time.sleep(3)

    @allure.story("Product page has h1")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_product_h1(self, driver):
        self._open_first_product(driver)
        page = MainPage(driver)
        title = page.product_title.get_text()
        assert title and title.strip()

    @allure.story("Product page has price")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_product_price(self, driver):
        self._open_first_product(driver)
        page = MainPage(driver)
        assert page.product_price.is_visible()

    @allure.story("Product page has Add to Cart")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_product_add_button(self, driver):
        self._open_first_product(driver)
        page = MainPage(driver)
        assert page.product_add_to_cart.is_visible()

    @allure.story("Product page has image")
    @allure.severity(allure.severity_level.NORMAL)
    def test_product_image(self, driver):
        self._open_first_product(driver)
        page = MainPage(driver)
        assert page.product_image.is_visible()

    @allure.story("Product page has description")
    @allure.severity(allure.severity_level.NORMAL)
    def test_product_description(self, driver):
        self._open_first_product(driver)
        page = MainPage(driver)
        assert page.product_description.is_visible()

    @allure.story("Product URL contains /products/")
    @allure.severity(allure.severity_level.NORMAL)
    def test_product_url(self, driver):
        self._open_first_product(driver)
        assert "/products/" in driver.current_url


@allure.epic("ADO Shop")
@allure.feature("Navigation")
class TestNavigation:

    @allure.story("Hibana collection loads")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_hibana_loads(self, driver):
        open_page(driver, "collections/hibana")
        assert "hibana" in driver.current_url

    @allure.story("Zanmu collection loads")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_zanmu_loads(self, driver):
        open_page(driver, "collections/2nd-original-album-zanmu")
        assert "zanmu" in driver.current_url

    @allure.story("Phantom Siita collection loads")
    @allure.severity(allure.severity_level.NORMAL)
    def test_phantom_siita_loads(self, driver):
        open_page(driver, "collections/phantom-siita")
        assert "phantom-siita" in driver.current_url

    @allure.story("Full navigation flow")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_full_navigation_flow(self, driver):
        page = open_page(driver, "collections/hibana")
        assert page.collection_product_items.count() > 0
        href = page.product_title_links[0].get_attribute("href")
        driver.get(href)
        time.sleep(3)
        product_page = MainPage(driver)
        assert product_page.product_title.get_text()
        driver.back()
        time.sleep(2)
        assert "hibana" in driver.current_url
