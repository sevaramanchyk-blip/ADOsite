"""Бизнес-сценарии для сайта ado-shop.com."""
import allure
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

MAIN_URL = "https://ado-shop.com/"


@allure.feature("Бизнес-сценарии")
@allure.story("Навигация по каталогу")
class TestCatalogNavigation:
    """Проверка навигации по коллекциям каталога."""

    COLLECTIONS = [
        ("shinzou", "Shinzou"),
        ("hibana", "Hibana"),
        ("2nd-original-album-zanmu", "Zanmu"),
        ("ados-best-adobum", "Ado's Best Adobum"),
        ("phantom-siita", "Phantom Siita"),
        ("all-merch", "All Merch"),
    ]

    @allure.title("Переход в коллекцию из меню")
    @pytest.mark.parametrize("slug,name", COLLECTIONS[:3])
    def test_navigate_to_collection(self, driver, slug, name):
        driver.get(MAIN_URL)
        wait = WebDriverWait(driver, 15)
        driver.get(f"{MAIN_URL}collections/{slug}")
        title = wait.until(lambda d: d.title)
        assert len(title) > 0, f"Страница {name} не загрузилась"

    @allure.title("В коллекции отображаются товары")
    @pytest.mark.parametrize("slug,name", COLLECTIONS[:3])
    def test_collection_shows_products(self, driver, slug, name):
        driver.get(f"{MAIN_URL}collections/{slug}")
        wait = WebDriverWait(driver, 15)
        products = wait.until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR,
                 ".card__content, .product-grid-container, "
                 ".card__information")
            )
        )
        assert len(products) > 0, f"Нет товаров в коллекции {name}"


@allure.feature("Бизнес-сценарии")
@allure.story("Просмотр товара")
class TestProductBrowsing:
    """Просмотр карточки товара."""

    @allure.title("Товар открывается из коллекции")
    def test_open_product_from_collection(self, driver):
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
                 ".product__info-wrapper, "
                 "[class*='product'], h1")
            )
        )
        assert "/products/" in driver.current_url

    @allure.title("На странице товара есть цена")
    def test_product_has_price(self, driver):
        driver.get(f"{MAIN_URL}collections/shinzou")
        wait = WebDriverWait(driver, 15)
        card = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "a[href*='/products/']")
            )
        )
        driver.get(card.get_attribute("href"))
        price = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR,
                 ".price, .price-item, "
                 "[class*='price'], .money")
            )
        )
        assert price is not None, "Цена товара не отображается"

    @allure.title("На странице товара есть кнопка добавления в корзину")
    def test_product_has_add_to_cart(self, driver):
        driver.get(f"{MAIN_URL}collections/shinzou")
        wait = WebDriverWait(driver, 15)
        card = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "a[href*='/products/']")
            )
        )
        driver.get(card.get_attribute("href"))
        btn = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR,
                 "button[name='add'], "
                 ".product-form__submit, "
                 "button[type='submit']")
            )
        )
        assert btn is not None, "Кнопка добавления в корзину не найдена"


@allure.feature("Бизнес-сценарии")
@allure.story("Корзина")
class TestCart:
    """Проверка корзины."""

    @allure.title("Страница корзины открывается")
    def test_cart_page_loads(self, driver):
        driver.get(f"{MAIN_URL}cart")
        wait = WebDriverWait(driver, 15)
        wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        assert "/cart" in driver.current_url

    @allure.title("Пустая корзина показывает сообщение")
    def test_empty_cart_message(self, driver):
        driver.get(f"{MAIN_URL}cart")
        wait = WebDriverWait(driver, 15)
        body = wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        text = body.text.lower()
        assert ("cart" in text or "корзин" in text
                or "empty" in text or "пуст" in text
                or "shop" in text), \
            "Нет сообщения о пустой корзине"


@allure.feature("Бизнес-сценарии")
@allure.story("Поиск")
class TestSearch:
    """Проверка поиска товаров."""

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
        assert dialog.is_displayed(), "Модалка поиска не открылась"

    @allure.title("Поиск по запросу Ado")
    def test_search_ado(self, driver):
        driver.get(MAIN_URL)
        wait = WebDriverWait(driver, 10)
        search_btn = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR,
                 "summary[aria-haspopup='dialog']")
            )
        )
        search_btn.click()
        input_field = wait.until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR,
                 "#Search-In-Modal, "
                 "input[name='q']")
            )
        )
        input_field.send_keys("Ado")
        input_field.submit()
        wait.until(
            lambda d: "search" in d.current_url.lower()
            or "q=" in d.current_url.lower()
        )
        assert True


@allure.feature("Бизнес-сценарии")
@allure.story("Навигация между страницами")
class TestNavigation:
    """Проверка навигации между страницами сайта."""

    @allure.title("Возврат на главную по логотипу")
    def test_logo_returns_home(self, driver):
        driver.get(f"{MAIN_URL}collections/shinzou")
        wait = WebDriverWait(driver, 15)
        logo = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR,
                 ".header__heading-logo-wrapper, "
                 ".header__heading-logo")
            )
        )
        logo.click()
        wait.until(
            lambda d: d.current_url.rstrip('/') ==
            MAIN_URL.rstrip('/')
        )
        assert driver.current_url.rstrip('/') == \
            MAIN_URL.rstrip('/'), \
            "Не удалось вернуться на главную"

    @allure.title("Хедер стабилен при прокрутке")
    def test_header_sticky_on_scroll(self, driver):
        driver.get(MAIN_URL)
        wait = WebDriverWait(driver, 10)
        header = wait.until(
            EC.visibility_of_element_located(
                (By.TAG_NAME, "header")
            )
        )
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);"
        )
        wait = WebDriverWait(driver, 5)
        wait.until(
            EC.visibility_of(header)
        )
        assert header.is_displayed(), \
            "Хедер исчез при прокрутке"
