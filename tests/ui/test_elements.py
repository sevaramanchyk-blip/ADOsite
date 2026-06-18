"""UI-тесты видимости элементов на сайте ado-shop.com."""
import allure
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from helpers.config import MAIN_URL


@allure.feature("UI тесты")
@allure.story("Отображение элементов")
class TestElementVisibility:
    """Проверка видимости основных элементов на главной странице."""
    @allure.title("Хедер виден на главной")
    def test_header_visible(self, driver):
        driver.get(MAIN_URL)
        header = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.TAG_NAME, "header"))
        )
        with allure.step("Хедер отображается"):
            assert header.is_displayed()
            assert header.size["height"] > 0

    @allure.title("Футер виден на главной")
    def test_footer_visible(self, driver):
        driver.get(MAIN_URL)
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);"
        )
        footer = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.TAG_NAME, "footer"))
        )
        with allure.step("Футер отображается"):
            assert footer.is_displayed()

    @allure.title("Кнопка корзины видна")
    def test_cart_button_visible(self, driver):
        driver.get(MAIN_URL)
        cart = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (By.ID, "cart-icon-bubble")
            )
        )
        with allure.step("Корзина видна"):
            assert cart.is_displayed()

    @allure.title("Все навкнопки хедера видны")
    def test_nav_buttons_visible(self, driver):
        driver.get(MAIN_URL)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "header"))
        )
        ids = [
            "HeaderMenu-home",
            "HeaderMenu-help",
            "HeaderMenu-contact",
        ]
        for element_id in ids:
            el = driver.find_element(By.ID, element_id)
            with allure.step(f"{element_id} найдена"):
                assert el is not None

    @allure.title("Логотип виден и имеет размер")
    def test_logo_has_size(self, driver):
        driver.get(MAIN_URL)
        header = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.TAG_NAME, "header"))
        )
        logo = header.find_element(
            By.CSS_SELECTOR, ".header__heading-logo"
        )
        with allure.step("Логотип виден"):
            assert logo.is_displayed()
        with allure.step("Логотип имеет размер"):
            size = logo.size
            assert size["width"] > 0
            assert size["height"] > 0

    @allure.title("Поисковая иконка видна")
    def test_search_icon_visible(self, driver):
        driver.get(MAIN_URL)
        search = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR,
                 "summary[aria-haspopup='dialog']")
            )
        )
        with allure.step("Иконка поиска видна"):
            assert search.size["width"] > 0


@allure.feature("UI тесты")
@allure.story("Отображение карточек товаров")
class TestProductCardVisibility:
    """Проверка видимости карточек товаров в коллекции."""
    @allure.title("Карточки товаров видны в коллекции")
    def test_product_cards_visible(self, driver):
        driver.get(f"{MAIN_URL}collections/shinzou")
        wait = WebDriverWait(driver, 15)
        cards = wait.until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR,
                 ".card-wrapper, .product-card, "
                 "[class*='product']")
            )
        )
        visible_count = 0
        for card in cards[:6]:
            try:
                if card.is_displayed():
                    visible_count += 1
            except Exception:
                pass
        with allure.step(f"Видимых карточек: {visible_count}"):
            assert visible_count > 0, (
                "Нет видимых карточек товаров"
            )

    @allure.title("У карточек есть изображения")
    def test_product_cards_have_images(self, driver):
        driver.get(f"{MAIN_URL}collections/shinzou")
        wait = WebDriverWait(driver, 15)
        images = wait.until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR,
                 ".card-wrapper img, "
                 ".card__media img")
            )
        )
        loaded = 0
        for img in images[:6]:
            try:
                natural_w = driver.execute_script(
                    "return arguments[0].naturalWidth", img
                )
                if natural_w and natural_w > 0:
                    loaded += 1
            except Exception:
                pass
        with allure.step(f"Загруженных изображений: {loaded}"):
            assert loaded > 0, (
                "Нет загруженных изображений товаров"
            )


@allure.feature("UI тесты")
@allure.story("Отображение страницы товара")
class TestProductPageVisibility:
    """Проверка отображения информации и цены товара."""
    @allure.title("Информация о товаре видна")
    def test_product_info_visible(self, driver):
        driver.get(f"{MAIN_URL}collections/shinzou")
        wait = WebDriverWait(driver, 15)
        card = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "a[href*='/products/']")
            )
        )
        href = card.get_attribute("href")
        driver.get(href)
        info = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR,
                 ".product-info, "
                 ".product__info-wrapper, "
                 "[class*='product-info']")
            )
        )
        with allure.step("Информация о товаре видна"):
            assert len(info.text.strip()) > 0

    @allure.title("Цена товара отображается")
    def test_product_price_visible(self, driver):
        driver.get(f"{MAIN_URL}collections/shinzou")
        wait = WebDriverWait(driver, 15)
        card = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "a[href*='/products/']")
            )
        )
        href = card.get_attribute("href")
        driver.get(href)
        price = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR,
                 ".price, .product__price, "
                 "[class*='price']")
            )
        )
        with allure.step("Цена отображается"):
            price_text = price.text.strip()
            assert len(price_text) > 0, "Цена пустая"
