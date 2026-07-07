"""
Тесты бизнес-логики ADO Shop.

Проверяют ключевые пользовательские сценарии:
работу корзины, выбор продуктов, функционал поиска.
"""

import time
import pytest
import allure
from selenium.webdriver.common.by import By
from helpers.config import BASE_URL
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


@allure.epic("ADO Shop Business Logic")
@allure.feature("Cart Flow")
class TestCartFlow:
    """Тесты сценариев корзины: пустая корзина, URL, кнопка checkout."""

    @allure.story("Empty cart message")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_cart_empty_message(self, driver):
        """На странице пустой корзины должно отображаться
        сообщение 'Your cart is empty'."""
        load_page(driver, "cart")
        msgs = driver.find_elements(
            By.XPATH, "//*[contains(text(),'Your cart is empty')]"
        )
        assert len(msgs) > 0, "Empty cart message not shown"

    @allure.story("Cart page URL")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_cart_url(self, driver):
        """URL страницы корзины должен содержать /cart."""
        load_page(driver, "cart")
        assert "/cart" in driver.current_url, "Not on cart page"

    @allure.story("Checkout button present on empty cart")
    @allure.severity(allure.severity_level.NORMAL)
    def test_checkout_on_empty_cart(self, driver):
        """Даже на пустой корзине должна быть кнопка checkout."""
        load_page(driver, "cart")
        btn = driver.find_elements(By.CSS_SELECTOR, 'button[name="checkout"]')
        assert len(btn) > 0, "Checkout button missing on empty cart"

    @allure.story("Cart icon in header")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_cart_icon_in_header(self, driver):
        """Иконка корзины должна быть видна в хедере."""
        p = load_page(driver)
        assert p.cart_link.is_visible(), "Cart icon not visible in header"


@allure.epic("ADO Shop Business Logic")
@allure.feature("Product Selection")
class TestProductSelection:
    """Тесты выбора продукта: наличие кнопки, цены, описания, изображения."""

    def _get_first_product_url(self, driver):
        """Вспомогательный метод: открывает коллекцию ALL MUSIC
        и возвращает URL первого товара."""
        load_page(driver, "collections/all")
        items = driver.find_elements(
            By.CSS_SELECTOR, "#product-grid li.grid__item a[href*='/products/']"
        )
        assert len(items) > 0, "No products found"
        return items[0].get_attribute("href")

    @allure.story("Product has add to cart button")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_add_to_cart_button(self, driver):
        """На странице продукта должна быть кнопка добавления в корзину."""
        href = self._get_first_product_url(driver)
        driver.get(href)
        time.sleep(3)
        btn = driver.find_elements(By.CSS_SELECTOR, 'button[name="add"]')
        assert len(btn) > 0, "Add to cart button missing"

    @allure.story("Product has price")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_product_has_price(self, driver):
        """На странице продукта должна отображаться цена
        (обычная или со скидкой)."""
        href = self._get_first_product_url(driver)
        driver.get(href)
        time.sleep(3)
        price = driver.find_elements(
            By.CSS_SELECTOR, ".price-item--regular, .price-item--sale"
        )
        assert len(price) > 0, "Product price not found"

    @allure.story("Product has title")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_product_has_title(self, driver):
        """На странице продукта должен быть непустой заголовок h1."""
        href = self._get_first_product_url(driver)
        driver.get(href)
        time.sleep(3)
        h1 = driver.find_elements(By.TAG_NAME, "h1")
        assert len(h1) > 0 and h1[0].text.strip(), "Product title missing"

    @allure.story("Product has description")
    @allure.severity(allure.severity_level.NORMAL)
    def test_product_has_description(self, driver):
        """На странице продукта должно быть описание."""
        href = self._get_first_product_url(driver)
        driver.get(href)
        time.sleep(3)
        desc = driver.find_elements(
            By.CSS_SELECTOR, ".product__description"
        )
        assert len(desc) > 0, "Product description missing"

    @allure.story("Product has image")
    @allure.severity(allure.severity_level.NORMAL)
    def test_product_has_image(self, driver):
        """На странице продукта должно быть изображение."""
        href = self._get_first_product_url(driver)
        driver.get(href)
        time.sleep(3)
        img = driver.find_elements(By.CSS_SELECTOR, ".product__media img")
        assert len(img) > 0, "Product image missing"

    @allure.story("Product image has src")
    @allure.severity(allure.severity_level.MINOR)
    def test_product_image_has_src(self, driver):
        """У изображения продукта должен быть валидный src-атрибут."""
        href = self._get_first_product_url(driver)
        driver.get(href)
        time.sleep(3)
        img = driver.find_elements(By.CSS_SELECTOR, ".product__media img")
        assert len(img) > 0
        src = img[0].get_attribute("src")
        assert src and src.startswith("http"), "Product image has no valid src"


@allure.epic("ADO Shop Business Logic")
@allure.feature("Search Flow")
class TestSearchFlow:
    """Тесты функционала поиска: поиск с результатами и без."""

    @allure.story("Search finds products")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_returns_results(self, driver):
        """Поиск по запросу 'Zanmu' должен показать результаты."""
        p = load_page(driver)
        p.search_toggle.click()
        p.search_input.send_keys("Zanmu")
        time.sleep(3)
        assert p.search_results.is_visible(), "No search results shown"

    @allure.story("Search with no results")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_no_results(self, driver):
        """Поиск по несуществующему запросу должен показать
        сообщение об отсутствии результатов."""
        p = load_page(driver)
        p.search_toggle.click()
        p.search_input.send_keys("zzzznonexistent12345")
        time.sleep(3)
        results = driver.find_elements(
            By.XPATH, "//*[contains(text(),'No results')]"
        )
        assert len(results) > 0, "No-results message not shown for invalid query"
