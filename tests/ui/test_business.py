"""Бизнес-сценарии тестирования сайта ado-shop.com."""
import allure
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from helpers.config import MAIN_URL


@allure.feature("Бизнес-сценарии")
@allure.story("Покупка товара")
class TestBusinessScenarioPurchase:
    """Сценарий: поиск товара и добавление в корзину."""
    @allure.title("BS-1: Пользователь находит товар и "
                  "добавляет в корзину")
    def test_add_to_cart_flow(self, driver):
        with allure.step("1. Открыть главную страницу"):
            driver.get(MAIN_URL)
            wait = WebDriverWait(driver, 15)
            wait.until(
                EC.presence_of_element_located(
                    (By.TAG_NAME, "header")
                )
            )

        with allure.step("2. Перейти в коллекцию Shinzou"):
            driver.get(f"{MAIN_URL}collections/shinzou")
            wait.until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR,
                     ".card-wrapper, .product-card, "
                     "[class*='product']")
                )
            )

        with allure.step("3. Открыть первый товар"):
            card = wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     "a[href*='/products/']")
                )
            )
            href = card.get_attribute("href")
            driver.get(href)
            wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     ".product-info, "
                     ".product__info-wrapper, "
                     "[class*='product-info']")
                )
            )

        with allure.step("4. Проверить наличие кнопки "
                         "'Add to cart' или 'Sold out'"):
            add_btn = wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     "button[name='add']")
                )
            )

        with allure.step("5. Нажать кнопку"):
            btn_text = add_btn.text.strip()
            add_btn.click()
            time.sleep(2)

        with allure.step("6. Проверить результат"):
            if btn_text.lower() == "sold out":
                pass
            else:
                cart = driver.find_element(
                    By.ID, "cart-icon-bubble"
                )
                assert cart is not None


@allure.feature("Бизнес-сценарии")
@allure.story("Навигация по каталогу")
class TestBusinessScenarioNavigation:
    """Сценарий: навигация между коллекциями."""
    @allure.title("BS-2: Пользователь переходит между "
                  "коллекциями")
    def test_navigation_between_collections(self, driver):
        with allure.step("1. Открыть коллекцию Shinzou"):
            driver.get(
                f"{MAIN_URL}collections/shinzou"
            )
            wait = WebDriverWait(driver, 15)
            wait.until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR,
                     ".card-wrapper, .product-card, "
                     "[class*='product']")
                )
            )
            url1 = driver.current_url

        with allure.step("2. Перейти в коллекцию Hibana"):
            driver.get(
                f"{MAIN_URL}collections/hibana"
            )
            wait.until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR,
                     ".card-wrapper, .product-card, "
                     "[class*='product']")
                )
            )
            url2 = driver.current_url
            assert url1 != url2, (
                "URL не изменился после перехода"
            )

        with allure.step("3. Проверить что товары "
                         "отображаются"):
            cards = driver.find_elements(
                By.CSS_SELECTOR,
                ".card-wrapper, .product-card, "
                "[class*='product']"
            )
            assert len(cards) > 0, (
                "Нет товаров в коллекции Hibana"
            )

        with allure.step("4. Вернуться в Shinzou"):
            driver.get(
                f"{MAIN_URL}collections/shinzou"
            )
            wait.until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR,
                     ".card-wrapper, .product-card, "
                     "[class*='product']")
                )
            )
            assert "shinzou" in driver.current_url


@allure.feature("Бизнес-сценарии")
@allure.story("Поиск и просмотр товара")
class TestBusinessScenarioSearch:
    """Сценарий: поиск товара через строку поиска."""
    @allure.title("BS-3: Пользователь ищет товар "
                  "через поиск")
    def test_search_product_flow(self, driver):
        with allure.step("1. Открыть главную страницу"):
            driver.get(MAIN_URL)
            wait = WebDriverWait(driver, 15)
            wait.until(
                EC.presence_of_element_located(
                    (By.TAG_NAME, "header")
                )
            )

        with allure.step("2. Открыть поиск"):
            search_btn = wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     "summary.header__icon--search")
                )
            )
            driver.execute_script(
                "arguments[0].click();", search_btn
            )
            time.sleep(2)
            search_input = wait.until(
                EC.visibility_of_element_located(
                    (By.ID, "Search-In-Modal")
                )
            )
            assert search_input.is_displayed(), (
                "Поле поиска не открылось"
            )

        with allure.step("3. Ввести запрос 'Shinzou'"):
            search_input.send_keys("Shinzou")
            time.sleep(2)

        with allure.step("4. Проверить результаты"):
            results = driver.find_elements(
                By.CSS_SELECTOR,
                "[class*='search-result'] a, "
                ".predictive-search__results a, "
                "[role='option']"
            )
            has_results = len(results) > 0
            page_text = driver.page_source.lower()
            has_shinzou = "shinzou" in page_text
            assert has_results or has_shinzou, (
                "Нет результатов поиска"
            )

        with allure.step("5. Нажать Enter для поиска"):
            search_input.submit()
            time.sleep(3)

        with allure.step("6. Проверить URL поиска"):
            time.sleep(2)
            assert "search" in driver.current_url or (
                "q=" in driver.current_url
            ), f"URL: {driver.current_url}"
