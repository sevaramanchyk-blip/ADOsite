"""
Расширенные UI-тесты ADO Shop.

Проверяют время загрузки страниц, корректность изображений
(src, alt), ссылок (href, HTTPS), скроллинг и заголовки страниц.
"""

import time
import pytest
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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


@allure.epic("ADO Shop Extended UI")
@allure.feature("Page Load")
class TestPageLoad:
    """Тесты загрузки страниц: время, readyState."""

    @allure.story("Homepage loads within timeout")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_homepage_load_time(self, driver):
        """Главная страница должна загрузиться менее чем за 15 секунд."""
        start = time.time()
        load_page(driver)
        elapsed = time.time() - start
        assert elapsed < 15, f"Homepage took {elapsed:.1f}s (>15s)"

    @allure.story("Ready state is complete")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_ready_state(self, driver):
        """document.readyState должен быть 'complete'
        после загрузки главной страницы."""
        load_page(driver)
        state = driver.execute_script("return document.readyState")
        assert state == "complete", f"ReadyState is '{state}'"

    @allure.story("Collection page loads")
    @allure.severity(allure.severity_level.NORMAL)
    def test_collection_loads(self, driver):
        """Страница коллекции Hibana должна полностью загрузиться."""
        load_page(driver, "collections/hibana")
        state = driver.execute_script("return document.readyState")
        assert state == "complete", "Collection page not fully loaded"

    @allure.story("Product page loads")
    @allure.severity(allure.severity_level.NORMAL)
    def test_product_page_loads(self, driver):
        """Страница продукта должна полностью загрузиться."""
        load_page(driver, "collections/all")
        items = driver.find_elements(
            By.CSS_SELECTOR,
            "#product-grid li.grid__item a[href*='/products/']"
        )
        assert len(items) > 0
        href = items[0].get_attribute("href")
        driver.get(href)
        time.sleep(3)
        state = driver.execute_script("return document.readyState")
        assert state == "complete", "Product page not fully loaded"


@allure.epic("ADO Shop Extended UI")
@allure.feature("Images")
class TestImages:
    """Тесты изображений: наличие src и alt атрибутов."""

    @allure.story("All images have src")
    @allure.severity(allure.severity_level.NORMAL)
    def test_images_have_src(self, driver):
        """У первых 10 изображений на главной странице
        должен быть атрибут src."""
        load_page(driver)
        imgs = driver.find_elements(By.TAG_NAME, "img")
        for img in imgs[:10]:
            src = img.get_attribute("src")
            assert src, "Image missing src attribute"

    @allure.story("Images have alt attribute")
    @allure.severity(allure.severity_level.MINOR)
    def test_images_have_alt(self, driver):
        """Большинство изображений на главной странице
        должны иметь атрибут alt (для accessibility)."""
        load_page(driver)
        imgs = driver.find_elements(By.TAG_NAME, "img")
        missing = 0
        for img in imgs[:10]:
            alt = img.get_attribute("alt")
            if not alt:
                missing += 1
        assert missing < len(imgs[:10]), \
            f"{missing}/{len(imgs[:10])} images missing alt"


@allure.epic("ADO Shop Extended UI")
@allure.feature("Links")
class TestLinks:
    """Тесты ссылок: наличие href, использование HTTPS."""

    @allure.story("All links have href")
    @allure.severity(allure.severity_level.MINOR)
    def test_links_have_href(self, driver):
        """Большинство ссылок на главной странице должны
        иметь атрибут href (не более 5 без href)."""
        load_page(driver)
        links = driver.find_elements(By.TAG_NAME, "a")
        missing = 0
        for link in links[:20]:
            href = link.get_attribute("href")
            if not href:
                missing += 1
        assert missing < 5, f"{missing} links missing href"

    @allure.story("Internal links use HTTPS")
    @allure.severity(allure.severity_level.MINOR)
    def test_internal_links_https(self, driver):
        """Внутренние ссылки (ado-shop.com) должны использовать HTTPS."""
        load_page(driver)
        links = driver.find_elements(By.TAG_NAME, "a")
        for link in links[:10]:
            href = link.get_attribute("href")
            if href and "ado-shop.com" in href:
                assert href.startswith("https://"), \
                    f"Internal link not HTTPS: {href}"


@allure.epic("ADO Shop Extended UI")
@allure.feature("Scrolling")
class TestScrolling:
    """Тесты скроллинга: прокрутка вниз и возврат наверх."""

    @allure.story("Scroll down works")
    @allure.severity(allure.severity_level.NORMAL)
    def test_scroll_down(self, driver):
        """Прокрутка вниз должна изменить scrollY > 0."""
        p = load_page(driver)
        p.scroll_down()
        scroll_y = driver.execute_script("return window.scrollY")
        assert scroll_y > 0, "Page did not scroll down"

    @allure.story("Scroll to top works")
    @allure.severity(allure.severity_level.NORMAL)
    def test_scroll_to_top(self, driver):
        """После прокрутки вниз и обратно scrollY должен быть 0."""
        p = load_page(driver)
        p.scroll_down()
        p.scroll_up()
        scroll_y = driver.execute_script("return window.scrollY")
        assert scroll_y == 0, f"Did not scroll to top, scrollY={scroll_y}"


@allure.epic("ADO Shop Extended UI")
@allure.feature("Page Title")
class TestPageTitle:
    """Тесты заголовков страниц (title тег)."""

    @allure.story("Homepage has title")
    @allure.severity(allure.severity_level.NORMAL)
    def test_homepage_title(self, driver):
        """Главная страница должна иметь непустой title."""
        load_page(driver)
        title = driver.title
        assert title, "Homepage has no title"

    @allure.story("Collection has title")
    @allure.severity(allure.severity_level.NORMAL)
    def test_collection_title(self, driver):
        """Страница коллекции должна иметь непустой title."""
        load_page(driver, "collections/all")
        title = driver.title
        assert title, "Collection page has no title"

    @allure.story("Cart has title")
    @allure.severity(allure.severity_level.NORMAL)
    def test_cart_title(self, driver):
        """Страница корзины должна иметь непустой title."""
        load_page(driver, "cart")
        title = driver.title
        assert title, "Cart page has no title"
