"""UI-тесты основных элементов сайта ado-shop.com."""
import allure
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

MAIN_URL = "https://ado-shop.com/"


@allure.feature("UI тесты")
@allure.story("Хедер")
class TestHeader:
    """Проверка элементов хедера: навигация, логотип, корзина."""
    @allure.title("Навигационные кнопки кликабельны")
    def test_header_nav_buttons(self, driver):
        driver.get(MAIN_URL)
        ids = [
            ("HeaderMenu-home", "Home"),
            ("HeaderMenu-music", "Music"),
            ("HeaderMenu-merch", "Merch"),
            ("HeaderMenu-help", "Help"),
            ("HeaderMenu-contact", "Contact"),
        ]
        for element_id, name in ids:
            el = driver.find_element(By.ID, element_id)
            with allure.step(f"Кнопка {name} кликабельна"):
                assert el.is_enabled(), f"{name} не кликабельна"

    @allure.title("Логотип отображается")
    def test_logo_visible(self, driver):
        driver.get(MAIN_URL)
        wait = WebDriverWait(driver, 10)
        header = wait.until(
            EC.visibility_of_element_located((By.TAG_NAME, "header"))
        )
        logo = header.find_element(
            By.CSS_SELECTOR, ".header__heading-logo"
        )
        with allure.step("Логотип виден"):
            assert logo.is_displayed()

    @allure.title("Корзина доступна")
    def test_cart_icon(self, driver):
        driver.get(MAIN_URL)
        cart = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.ID, "cart-icon-bubble")
            )
        )
        with allure.step("Иконка корзины есть"):
            assert cart is not None


@allure.feature("UI тесты")
@allure.story("Футер")
class TestFooter:
    """Проверка наличия и содержимого футера."""
    @allure.title("Футер присутствует на странице")
    def test_footer_exists(self, driver):
        driver.get(MAIN_URL)
        wait = WebDriverWait(driver, 10)
        footer = wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "footer"))
        )
        with allure.step("Футер найден"):
            assert footer is not None

    @allure.title("Копирайт в футере")
    def test_footer_copyright(self, driver):
        driver.get(MAIN_URL)
        wait = WebDriverWait(driver, 10)
        footer = wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "footer"))
        )
        text = footer.text.lower()
        with allure.step("Есть копирайт или название"):
            assert "ado" in text or "shopify" in text or "©" in text


@allure.feature("UI тесты")
@allure.story("Страницы коллекций")
class TestCollections:
    """Проверка загрузки страниц коллекций."""
    COLLECTIONS = [
        ("shinzou", "Shinzou"),
        ("hibana", "Hibana"),
        ("2nd-original-album-zanmu", "Zanmu"),
    ]

    @allure.title("Коллекция загружается")
    @pytest.mark.parametrize("slug,name", COLLECTIONS)
    def test_collection_loads(self, driver, slug, name):
        driver.get(f"{MAIN_URL}collections/{slug}")
        wait = WebDriverWait(driver, 15)
        with allure.step(f"Страница {name} загружена"):
            title = wait.until(lambda d: d.title)
            assert len(title) > 0

    @allure.title("В коллекции есть карточки товаров")
    @pytest.mark.parametrize("slug,name", COLLECTIONS)
    def test_collection_has_products(self, driver, slug, name):
        driver.get(f"{MAIN_URL}collections/{slug}")
        wait = WebDriverWait(driver, 15)
        cards = wait.until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR,
                 ".product-card, .card-wrapper, "
                 "[class*='product']")
            )
        )
        with allure.step(f"Найдены карточки в {name}"):
            assert len(cards) > 0, (
                f"Нет карточек товаров в {name}"
            )


@allure.feature("UI тесты")
@allure.story("Страница товара")
class TestProductPage:
    """Проверка открытия страницы товара из коллекции."""
    @allure.title("Товар открывается из коллекции")
    def test_product_from_collection(self, driver):
        driver.get(f"{MAIN_URL}collections/shinzou")
        wait = WebDriverWait(driver, 15)
        card = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "a[href*='/products/']")
            )
        )
        href = card.get_attribute("href")
        driver.get(href)
        wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR,
                 ".product-info, .product__info-wrapper, "
                 "[class*='product-info']")
            )
        )
        with allure.step("Страница товара открыта"):
            assert "/products/" in driver.current_url


@allure.feature("UI тесты")
@allure.story("Поиск")
class TestSearch:
    """Проверка работы поиска на сайте."""
    @allure.title("Поиск открывается по клику")
    def test_search_opens(self, driver):
        driver.get(MAIN_URL)
        wait = WebDriverWait(driver, 10)
        search_btn = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR,
                 "summary[aria-haspopup='dialog']")
            )
        )
        search_btn.click()
        dialog = wait.until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR,
                 "search-modal, [role='dialog'], "
                 ".search-modal")
            )
        )
        with allure.step("Модалка поиска открыта"):
            assert dialog.is_displayed()


@allure.feature("UI тесты")
@allure.story("Размер страницы")
class TestPageSize:
    """Проверка размера главной страницы."""
    @allure.title("Главная страница < 5MB")
    def test_main_page_size(self, driver):
        driver.get(MAIN_URL)
        size = len(driver.page_source.encode("utf-8"))
        with allure.step(f"Размер страницы: {size / 1024:.0f} KB"):
            assert size < 5 * 1024 * 1024, (
                f"Страница слишком тяжёлая: {size / 1024:.0f} KB"
            )
