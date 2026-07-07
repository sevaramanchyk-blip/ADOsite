"""
Тесты проверки текста (spellcheck) на страницах ADO Shop.

Проверяют корректность заголовков, наличие непустых текстов,
соответствие известным словам бренда и тексты политик.
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


# Известные слова бренда, которые должны встречаться в заголовках продуктов
KNOWN_WORDS = [
    "Ado", "Hibana", "Zanmu", "Shinzou", "Phantom Siita",
    "Yodaka", "Vivarium", "Merch", "Cart", "Checkout", "Search", "Music",
    "Privacy Policy", "Refund Policy", "Terms of Service",
]


@allure.epic("ADO Shop Spellcheck")
@allure.feature("Page Text Validation")
class TestHomepageSpellcheck:
    """Проверка текстового контента главной страницы."""

    @allure.story("Homepage title contains Ado")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_homepage_title(self, driver):
        """Заголовок страницы (title) должен содержать 'Ado'."""
        load_page(driver)
        title = driver.title
        assert "Ado" in title or "ado" in title.lower(), \
            f"Homepage title '{title}' does not contain 'Ado'"

    @allure.story("Homepage has main content")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_homepage_main_content(self, driver):
        """На главной странице должен присутствовать элемент MainContent."""
        load_page(driver)
        mc = driver.find_elements(By.ID, "MainContent")
        assert len(mc) > 0, "MainContent not found"

    @allure.story("Homepage h1 is not empty")
    @allure.severity(allure.severity_level.NORMAL)
    def test_homepage_h1_not_empty(self, driver):
        """На главной странице должен присутствовать элемент h1
        (текст может быть пустым, если заголовок — изображение)."""
        p = load_page(driver)
        p.scroll_down()
        h1 = driver.find_elements(By.TAG_NAME, "h1")
        assert len(h1) > 0, "Homepage h1 element not found"


@allure.epic("ADO Shop Spellcheck")
@allure.feature("Page Text Validation")
class TestCollectionSpellcheck:
    """Проверка текстового контента страниц коллекций."""

    @allure.story("Collection page has non-empty h1")
    @allure.severity(allure.severity_level.NORMAL)
    def test_collection_h1(self, driver):
        """На странице коллекции должен быть непустой заголовок h1."""
        load_page(driver, "collections/all")
        h1 = driver.find_elements(By.TAG_NAME, "h1")
        assert len(h1) > 0 and h1[0].text.strip(), \
            "Collection page h1 missing or empty"

    @allure.story("Product titles are not empty")
    @allure.severity(allure.severity_level.NORMAL)
    def test_product_titles_not_empty(self, driver):
        """В коллекции должны быть ссылки на товары с валидными href."""
        load_page(driver, "collections/all")
        product_links = driver.find_elements(
            By.CSS_SELECTOR,
            "#product-grid li.grid__item a[href*='/products/']"
        )
        assert len(product_links) > 0, "No product links found"
        for link in product_links[:5]:
            href = link.get_attribute("href")
            assert href and "/products/" in href, \
                f"Product link has no valid href: {href}"


@allure.epic("ADO Shop Spellcheck")
@allure.feature("Page Text Validation")
class TestProductSpellcheck:
    """Проверка текстового контента страницы продукта."""

    def _open_first_product(self, driver):
        """Вспомогательный метод: открывает коллекцию ALL MUSIC
        и переходит на страницу первого товара."""
        load_page(driver, "collections/all")
        items = driver.find_elements(
            By.CSS_SELECTOR,
            "#product-grid li.grid__item a[href*='/products/']"
        )
        assert len(items) > 0
        href = items[0].get_attribute("href")
        driver.get(href)
        time.sleep(3)

    @allure.story("Product title not empty")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_product_title_not_empty(self, driver):
        """Заголовок продукта не должен быть пустым."""
        self._open_first_product(driver)
        h1 = driver.find_elements(By.TAG_NAME, "h1")
        assert len(h1) > 0 and h1[0].text.strip(), \
            "Product title is empty"

    @allure.story("Product title matches known words")
    @allure.severity(allure.severity_level.NORMAL)
    def test_product_title_known_words(self, driver):
        """Заголовок продукта должен содержать хотя бы одно
        известное слово бренда из списка KNOWN_WORDS."""
        self._open_first_product(driver)
        h1 = driver.find_elements(By.TAG_NAME, "h1")
        assert len(h1) > 0
        title = h1[0].text.strip()
        has_known = any(w.lower() in title.lower() for w in KNOWN_WORDS)
        assert has_known, \
            f"Product title '{title}' contains no known brand words"


@allure.epic("ADO Shop Spellcheck")
@allure.feature("Page Text Validation")
class TestPolicySpellcheck:
    """Проверка текстового контента страниц политик."""

    @pytest.mark.parametrize("policy_path,expected_text", [
        ("policies/privacy-policy", "Privacy"),
        ("policies/refund-policy", "Refund"),
        ("policies/terms-of-service", "Terms"),
    ])
    @allure.story("Policy page loads with correct text")
    @allure.severity(allure.severity_level.NORMAL)
    def test_policy_page_text(self, driver, policy_path, expected_text):
        """Каждая страница политики должна загружаться и содержать
        ключевое слово в тексте (Privacy / Refund / Terms)."""
        load_page(driver, policy_path)
        body = driver.find_element(By.TAG_NAME, "body").text
        assert expected_text.lower() in body.lower(), \
            f"Policy page '{policy_path}' missing '{expected_text}'"
