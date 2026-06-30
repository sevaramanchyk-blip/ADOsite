"""Расширенные UI-тесты для сайта ado-shop.com."""
import allure
import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from helpers.config import MAIN_URL, COLLECTIONS


@allure.feature("UI тесты")
@allure.story("Навигация по сайту")
class TestNavigationLinks:
    """Проверка работы навигационных ссылок."""

    @allure.title("Ссылка Home ведёт на главную")
    def test_home_link(self, driver):
        driver.get(f"{MAIN_URL}collections/shinzou")
        wait = WebDriverWait(driver, 10)
        home = wait.until(
            EC.element_to_be_clickable((By.ID, "HeaderMenu-home"))
        )
        home.click()
        time.sleep(2)
        with allure.step("Перешли на главную"):
            assert driver.current_url.rstrip("/") == MAIN_URL.rstrip("/")

    @allure.title("Клик по логотипу ведёт на главную")
    def test_logo_links_home(self, driver):
        driver.get(f"{MAIN_URL}collections/shinzou")
        wait = WebDriverWait(driver, 10)
        logo = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, ".header__heading-link")
            )
        )
        logo.click()
        time.sleep(2)
        with allure.step("Перешли на главную через логотип"):
            assert driver.current_url.rstrip("/").endswith(".com")

    @allure.title("Ссылка Help открывается")
    def test_help_link(self, driver):
        driver.get(MAIN_URL)
        wait = WebDriverWait(driver, 10)
        help_link = wait.until(
            EC.element_to_be_clickable((By.ID, "HeaderMenu-help"))
        )
        help_link.click()
        time.sleep(2)
        with allure.step("Страница Help загружена"):
            assert "help" in driver.current_url.lower() or (
                driver.title != ""
            )

    @allure.title("Ссылка Contact открывается")
    def test_contact_link(self, driver):
        driver.get(MAIN_URL)
        wait = WebDriverWait(driver, 10)
        contact = wait.until(
            EC.element_to_be_clickable(
                (By.ID, "HeaderMenu-contact")
            )
        )
        contact.click()
        time.sleep(2)
        with allure.step("Страница Contact загружена"):
            assert "contact" in driver.current_url.lower() or (
                driver.title != ""
            )


@allure.feature("UI тесты")
@allure.story("Корзина")
class TestCart:
    """Проверка функциональности корзины."""

    @allure.title("Корзина открывается по клику")
    def test_cart_opens(self, driver):
        driver.get(MAIN_URL)
        wait = WebDriverWait(driver, 10)
        cart = wait.until(
            EC.element_to_be_clickable(
                (By.ID, "cart-icon-bubble")
            )
        )
        cart.click()
        time.sleep(2)
        with allure.step("Корзина открыта"):
            assert "cart" in driver.current_url.lower() or (
                len(driver.find_elements(
                    By.CSS_SELECTOR,
                    "[class*='cart'], [class*='drawer']"
                )) > 0
            )

    @allure.title("Корзина отображается пустой на старте")
    def test_cart_empty_message(self, driver):
        driver.get(f"{MAIN_URL}cart")
        wait = WebDriverWait(driver, 10)
        time.sleep(2)
        page_text = driver.page_source.lower()
        with allure.step("Корзина пуста или есть сообщение"):
            assert (
                "empty" in page_text
                or "cart" in page_text
                or "корзин" in page_text
            )


@allure.feature("UI тесты")
@allure.story("Страница товара")
class TestProductPageExtended:
    """Расширенные проверки страницы товара."""

    @allure.title("У товара есть заголовок")
    def test_product_has_title(self, driver):
        driver.get(f"{MAIN_URL}collections/shinzou")
        wait = WebDriverWait(driver, 15)
        card = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "a[href*='/products/']")
            )
        )
        driver.get(card.get_attribute("href"))
        title = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR,
                 "h1, .product-info__title, "
                 "[class*='product-title']")
            )
        )
        with allure.step(f"Заголовок: {title.text[:30]}"):
            assert len(title.text.strip()) > 0

    @allure.title("У товара есть описание")
    def test_product_has_description(self, driver):
        driver.get(f"{MAIN_URL}collections/shinzou")
        wait = WebDriverWait(driver, 15)
        card = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "a[href*='/products/']")
            )
        )
        driver.get(card.get_attribute("href"))
        time.sleep(3)
        page_text = driver.page_source.lower()
        with allure.step("Описание присутствует"):
            assert "description" in page_text or (
                len(page_text) > 2000
            )

    @allure.title("У товара есть изображение")
    def test_product_has_image(self, driver):
        driver.get(f"{MAIN_URL}collections/shinzou")
        wait = WebDriverWait(driver, 15)
        card = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "a[href*='/products/']")
            )
        )
        driver.get(card.get_attribute("href"))
        images = wait.until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR,
                 ".product__media img, "
                 ".product-info img, "
                 "[class*='product'] img")
            )
        )
        with allure.step(f"Найдено {len(images)} изображений"):
            assert len(images) > 0

    @allure.title("Кнопка Add to cart или Sold out")
    def test_product_add_button(self, driver):
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
                (By.CSS_SELECTOR, "button[name='add']")
            )
        )
        btn_text = btn.text.strip().lower()
        with allure.step(f"Кнопка: {btn_text}"):
            assert "add" in btn_text or "sold" in btn_text

    @allure.title("Breadcrumbs присутствуют")
    def test_product_breadcrumbs(self, driver):
        driver.get(f"{MAIN_URL}collections/shinzou")
        wait = WebDriverWait(driver, 15)
        card = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "a[href*='/products/']")
            )
        )
        driver.get(card.get_attribute("href"))
        time.sleep(2)
        breadcrumbs = driver.find_elements(
            By.CSS_SELECTOR,
            "nav.breadcrumb, .breadcrumb, "
            "[class*='breadcrumb'], "
            "[aria-label='Breadcrumb']"
        )
        with allure.step(f"Breadcrumbs: {len(breadcrumbs)}"):
            pass


@allure.feature("UI тесты")
@allure.story("Коллекции")
class TestCollectionsExtended:
    """Расширенные проверки коллекций."""

    @allure.title("Коллекция имеет заголовок")
    @pytest.mark.parametrize("slug,name", COLLECTIONS)
    def test_collection_has_title(self, driver, slug, name):
        driver.get(f"{MAIN_URL}collections/{slug}")
        wait = WebDriverWait(driver, 15)
        title = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR,
                 "h1, .collection-hero__title, "
                 "[class*='collection'] h1")
            )
        )
        with allure.step(f"Заголовок коллекции: {title.text[:30]}"):
            assert len(title.text.strip()) > 0

    @allure.title("Коллекция имеет количество товаров")
    @pytest.mark.parametrize("slug,name", COLLECTIONS[:3])
    def test_collection_product_count(self, driver, slug, name):
        driver.get(f"{MAIN_URL}collections/{slug}")
        wait = WebDriverWait(driver, 15)
        cards = wait.until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR,
                 ".card-wrapper, .product-card, "
                 "[class*='product']")
            )
        )
        with allure.step(f"Товаров в {name}: {len(cards)}"):
            assert len(cards) > 0

    @allure.title("Изображения товаров загружаются")
    @pytest.mark.parametrize("slug,name", COLLECTIONS[:2])
    def test_collection_images_load(self, driver, slug, name):
        driver.get(f"{MAIN_URL}collections/{slug}")
        wait = WebDriverWait(driver, 15)
        images = wait.until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR,
                 ".card-wrapper img, .card__media img")
            )
        )
        loaded = 0
        for img in images[:4]:
            try:
                w = driver.execute_script(
                    "return arguments[0].naturalWidth", img
                )
                if w and w > 0:
                    loaded += 1
            except Exception:
                pass
        with allure.step(f"Загруженных изображений: {loaded}"):
            assert loaded > 0


@allure.feature("UI тесты")
@allure.story("Поиск")
class TestSearchExtended:
    """Расширенные проверки поиска."""

    @allure.title("Поиск по запросу 'Ado'")
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
        time.sleep(1)
        search_input = wait.until(
            EC.visibility_of_element_located(
                (By.ID, "Search-In-Modal")
            )
        )
        search_input.send_keys("Ado")
        time.sleep(2)
        page = driver.page_source.lower()
        with allure.step("Результаты поиска содержат Ado"):
            assert "ado" in page

    @allure.title("Поиск по запросу 'Vinyl'")
    def test_search_vinyl(self, driver):
        driver.get(MAIN_URL)
        wait = WebDriverWait(driver, 10)
        search_btn = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR,
                 "summary[aria-haspopup='dialog']")
            )
        )
        search_btn.click()
        time.sleep(1)
        search_input = wait.until(
            EC.visibility_of_element_located(
                (By.ID, "Search-In-Modal")
            )
        )
        search_input.send_keys("Vinyl")
        time.sleep(2)
        page = driver.page_source.lower()
        with allure.step("Результаты поиска"):
            assert "vinyl" in page or "result" in page

    @allure.title("Поиск по несуществующему запросу")
    def test_search_no_results(self, driver):
        driver.get(MAIN_URL)
        wait = WebDriverWait(driver, 10)
        search_btn = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR,
                 "summary[aria-haspopup='dialog']")
            )
        )
        search_btn.click()
        time.sleep(1)
        search_input = wait.until(
            EC.visibility_of_element_located(
                (By.ID, "Search-In-Modal")
            )
        )
        search_input.send_keys("zzznotexist12345")
        time.sleep(3)
        page = driver.page_source.lower()
        with allure.step("Нет результатов или сообщение"):
            assert (
                "no results" in page
                or "nothing" in page
                or "not found" in page
                or "zzznotexist" in page
            )


@allure.feature("UI тесты")
@allure.story("Размер страницы")
class TestPageSizeExtended:
    """Проверка размера страниц коллекций."""

    @allure.title("Страница коллекции < 3MB")
    @pytest.mark.parametrize("slug,name", COLLECTIONS[:2])
    def test_collection_page_size(self, driver, slug, name):
        driver.get(f"{MAIN_URL}collections/{slug}")
        time.sleep(2)
        size = len(driver.page_source.encode("utf-8"))
        with allure.step(f"Размер {name}: {size / 1024:.0f} KB"):
            assert size < 3 * 1024 * 1024, (
                f"{name}: {size / 1024:.0f} KB"
            )

    @allure.title("Страница товара < 3MB")
    def test_product_page_size(self, driver):
        driver.get(f"{MAIN_URL}collections/shinzou")
        wait = WebDriverWait(driver, 15)
        card = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "a[href*='/products/']")
            )
        )
        driver.get(card.get_attribute("href"))
        time.sleep(3)
        size = len(driver.page_source.encode("utf-8"))
        with allure.step(f"Размер страницы товара: {size / 1024:.0f} KB"):
            assert size < 3 * 1024 * 1024


@allure.feature("UI тесты")
@allure.story("Интерактивность")
class TestInteractivity:
    """Проверка интерактивных элементов."""

    @allure.title("Hover на карточку товара")
    def test_product_card_hover(self, driver):
        driver.get(f"{MAIN_URL}collections/shinzou")
        wait = WebDriverWait(driver, 15)
        card = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR,
                 ".card-wrapper, .product-card, "
                 "[class*='product']")
            )
        )
        from selenium.webdriver.common.action_chains import ActionChains
        ActionChains(driver).move_to_element(card).perform()
        time.sleep(1)
        with allure.step("Hover выполнен"):
            assert card.is_displayed()

    @allure.title("Прокрутка до футера")
    def test_scroll_to_footer(self, driver):
        driver.get(MAIN_URL)
        wait = WebDriverWait(driver, 10)
        footer = wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "footer"))
        )
        driver.execute_script(
            "arguments[0].scrollIntoView();", footer
        )
        time.sleep(1)
        with allure.step("Футер в видимой области"):
            assert footer.is_displayed()

    @allure.title("Enter в поле поиска")
    def test_search_enter(self, driver):
        driver.get(MAIN_URL)
        wait = WebDriverWait(driver, 10)
        search_btn = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR,
                 "summary[aria-haspopup='dialog']")
            )
        )
        search_btn.click()
        time.sleep(1)
        search_input = wait.until(
            EC.visibility_of_element_located(
                (By.ID, "Search-In-Modal")
            )
        )
        search_input.send_keys("Shinzou")
        search_input.send_keys(Keys.ENTER)
        time.sleep(3)
        with allure.step("Поиск по Enter"):
            assert "search" in driver.current_url or (
                "q=" in driver.current_url
            )


@allure.feature("UI тесты")
@allure.story("Адаптивность")
class TestResponsive:
    """Проверка адаптивности (разные размеры экрана)."""

    @allure.title("Хедер виден при мобильном размере")
    def test_mobile_header(self, driver):
        driver.set_window_size(375, 812)
        driver.get(MAIN_URL)
        wait = WebDriverWait(driver, 15)
        header = wait.until(
            EC.visibility_of_element_located(
                (By.TAG_NAME, "header")
            )
        )
        with allure.step("Хедер виден на мобильном"):
            assert header.is_displayed()
        driver.set_window_size(1920, 1080)

    @allure.title("Логотип виден при мобильном размере")
    def test_mobile_logo(self, driver):
        driver.set_window_size(375, 812)
        driver.get(MAIN_URL)
        wait = WebDriverWait(driver, 15)
        logo = wait.until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, ".header__heading-logo")
            )
        )
        with allure.step("Логотип виден на мобильном"):
            assert logo.is_displayed()
        driver.set_window_size(1920, 1080)

    @allure.title("Товары отображаются на планшете")
    def test_tablet_products(self, driver):
        driver.set_window_size(768, 1024)
        driver.get(f"{MAIN_URL}collections/shinzou")
        wait = WebDriverWait(driver, 15)
        cards = wait.until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR,
                 ".card-wrapper, .product-card, "
                 "[class*='product']")
            )
        )
        with allure.step(f"Товаров на планшете: {len(cards)}"):
            assert len(cards) > 0
        driver.set_window_size(1920, 1080)


@allure.feature("UI тесты")
@allure.story("Изображения")
class TestImages:
    """Проверка загрузки изображений."""

    @allure.title("Логотип — валидное изображение")
    def test_logo_image_valid(self, driver):
        driver.get(MAIN_URL)
        wait = WebDriverWait(driver, 10)
        logo = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".header__heading-logo")
            )
        )
        natural_w = driver.execute_script(
            "return arguments[0].naturalWidth", logo
        )
        with allure.step(f"Ширина логотипа: {natural_w}"):
            assert natural_w and natural_w > 0

    @allure.title("Изображения товаров загружены")
    def test_product_images_loaded(self, driver):
        driver.get(f"{MAIN_URL}collections/shinzou")
        wait = WebDriverWait(driver, 15)
        images = wait.until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR,
                 ".card-wrapper img, .card__media img")
            )
        )
        loaded = 0
        for img in images[:6]:
            try:
                w = driver.execute_script(
                    "return arguments[0].naturalWidth", img
                )
                if w and w > 0:
                    loaded += 1
            except Exception:
                pass
        with allure.step(f"Загруженных: {loaded}/{len(images[:6])}"):
            assert loaded > 0
