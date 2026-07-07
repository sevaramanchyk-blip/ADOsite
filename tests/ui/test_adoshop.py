"""
Тесты магазина ADO Shop: коллекции, страницы продуктов, навигация.

Проверяют загрузку всех коллекций по slug, корректность
отображения страниц продуктов и полный поток навигации.
"""

import time
import pytest
import allure
from selenium.webdriver.common.by import By
from helpers.config import BASE_URL, COLLECTIONS
from core.locators.main_locators import MainPage


def load_page(driver, path=""):
    """
    Утилита: открывает страницу по пути и возвращает объект MainPage
    без полной инициализации (через __new__), чтобы избежать
    лишнего ожидания загрузки из конструктора WebPage.
    """
    url = f"{BASE_URL}/{path}" if path else BASE_URL
    driver.get(url)
    time.sleep(3)
    p = MainPage.__new__(MainPage)
    p._web_driver = driver
    return p


@allure.epic("ADO Shop")
@allure.feature("Collections")
class TestCollections:
    """Тесты загрузки коллекций товаров."""

    @allure.story("ALL MUSIC collection loads")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_all_music(self, driver):
        """Коллекция ALL MUSIC (/collections/all) должна загрузиться
        и содержать сетку продуктов."""
        load_page(driver, "collections/all")
        grid = driver.find_elements(By.ID, "product-grid")
        assert len(grid) > 0, "ALL MUSIC grid not found"

    @allure.story("Collection has product items")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_collection_has_products(self, driver):
        """Коллекция ALL MUSIC должна содержать хотя бы один товар."""
        load_page(driver, "collections/all")
        items = driver.find_elements(
            By.CSS_SELECTOR, "#product-grid li.grid__item"
        )
        assert len(items) > 0, "No product items in collection"

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
        """Параметризованный тест: каждая коллекция по slug
        должна загружаться и содержать сетку продуктов."""
        load_page(driver, f"collections/{slug}")
        grid = driver.find_elements(By.ID, "product-grid")
        assert len(grid) > 0, f"Collection '{slug}' grid not found"


@allure.epic("ADO Shop")
@allure.feature("Product Pages")
class TestProductPages:
    """Тесты страниц отдельных продуктов."""

    def _open_first_product(self, driver):
        """Вспомогательный метод: открывает коллекцию ALL MUSIC
        и переходит на страницу первого товара."""
        load_page(driver, "collections/all")
        items = driver.find_elements(
            By.CSS_SELECTOR,
            "#product-grid li.grid__item a[href*='/products/']"
        )
        assert len(items) > 0, "No products to open"
        href = items[0].get_attribute("href")
        driver.get(href)
        time.sleep(3)

    @allure.story("Product page has h1")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_product_h1(self, driver):
        """Страница продукта должна содержать заголовок h1."""
        self._open_first_product(driver)
        h1 = driver.find_elements(By.TAG_NAME, "h1")
        assert len(h1) > 0 and h1[0].text.strip(), "Product h1 missing"

    @allure.story("Product page has price")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_product_price(self, driver):
        """Страница продукта должна отображать цену."""
        self._open_first_product(driver)
        price = driver.find_elements(By.CSS_SELECTOR, ".price-item--regular")
        assert len(price) > 0, "Product price missing"

    @allure.story("Product page has Add to Cart")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_product_add_button(self, driver):
        """На странице продукта должна быть кнопка 'Add to Cart'."""
        self._open_first_product(driver)
        btn = driver.find_elements(By.CSS_SELECTOR, 'button[name="add"]')
        assert len(btn) > 0, "Add to Cart button missing"

    @allure.story("Product page has image")
    @allure.severity(allure.severity_level.NORMAL)
    def test_product_image(self, driver):
        """На странице продукта должно отображаться изображение."""
        self._open_first_product(driver)
        img = driver.find_elements(By.CSS_SELECTOR, ".product__media img")
        assert len(img) > 0, "Product image missing"

    @allure.story("Product page has description")
    @allure.severity(allure.severity_level.NORMAL)
    def test_product_description(self, driver):
        """На странице продукта должно быть описание."""
        self._open_first_product(driver)
        desc = driver.find_elements(By.CSS_SELECTOR, ".product__description")
        assert len(desc) > 0, "Product description missing"

    @allure.story("Product URL contains /products/")
    @allure.severity(allure.severity_level.NORMAL)
    def test_product_url(self, driver):
        """URL страницы продукта должен содержать /products/."""
        self._open_first_product(driver)
        assert "/products/" in driver.current_url, "Not on product page"


@allure.epic("ADO Shop")
@allure.feature("Navigation")
class TestNavigation:
    """Тесты навигации между страницами магазина."""

    @allure.story("Hibana collection loads")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_hibana_loads(self, driver):
        """Коллекция Hibana должна загружаться по URL."""
        load_page(driver, "collections/hibana")
        assert "hibana" in driver.current_url

    @allure.story("Zanmu collection loads")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_zanmu_loads(self, driver):
        """Коллекция Zanmu должна загружаться по URL."""
        load_page(driver, "collections/2nd-original-album-zanmu")
        assert "zanmu" in driver.current_url

    @allure.story("Phantom Siita collection loads")
    @allure.severity(allure.severity_level.NORMAL)
    def test_phantom_siita_loads(self, driver):
        """Коллекция Phantom Siita должна загружаться по URL."""
        load_page(driver, "collections/phantom-siita")
        assert "phantom-siita" in driver.current_url

    @allure.story("Full navigation flow")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_full_navigation_flow(self, driver):
        """
        Полный поток навигации:
        1. Открыть коллекцию Hibana
        2. Перейти на страницу первого продукта
        3. Убедиться, что h1 заголовок присутствует
        4. Вернуться назад и убедиться, что URL содержит 'hibana'
        """
        load_page(driver, "collections/hibana")
        items = driver.find_elements(
            By.CSS_SELECTOR,
            "#product-grid li.grid__item a[href*='/products/']"
        )
        assert len(items) > 0, "No products in Hibana"
        href = items[0].get_attribute("href")
        driver.get(href)
        time.sleep(3)
        h1 = driver.find_elements(By.TAG_NAME, "h1")
        assert len(h1) > 0, "No h1 on product page"
        driver.back()
        time.sleep(2)
        assert "hibana" in driver.current_url, "Did not return to Hibana"
