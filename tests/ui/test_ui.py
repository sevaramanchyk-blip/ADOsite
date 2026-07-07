import time
import pytest
import allure
from selenium.webdriver.common.by import By
from helpers.config import BASE_URL
from core.locators.main_locators import MainPage


def load_page(driver, path=""):
    """Navigate and wait without MainPage's heavy init."""
    url = f"{BASE_URL}/{path}" if path else BASE_URL
    driver.get(url)
    time.sleep(3)
    p = MainPage.__new__(MainPage)
    p._web_driver = driver
    return p


@allure.epic("ADO Shop UI Tests")
@allure.feature("Header Navigation")
class TestHeader:

    @allure.story("Header is visible")
    @allure.title("Проверка хедера")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_header_visible(self, driver):
        p = load_page(driver)
        assert p.header_element.is_visible()

    @allure.story("Navigation links present")
    @allure.title("Ссылки навигации")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_nav_links(self, driver):
        p = load_page(driver)
        assert p.nav_links.count() >= 5

    @allure.story("Cart link present")
    @allure.title("Ссылка корзины")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_cart_link(self, driver):
        p = load_page(driver)
        assert p.cart_link.is_visible()

    @allure.story("Cart navigates to /cart")
    @allure.title("Переход в корзину")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_cart_navigates(self, driver):
        p = load_page(driver)
        p.cart_link.click()
        assert "/cart" in driver.current_url


@allure.epic("ADO Shop UI Tests")
@allure.feature("Search")
class TestSearch:

    @allure.story("Search opens input")
    @allure.title("Открытие поиска")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_opens(self, driver):
        p = load_page(driver)
        p.search_toggle.click()
        assert p.search_input.is_visible()

    @allure.story("Search accepts text")
    @allure.title("Ввод текста")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_text(self, driver):
        p = load_page(driver)
        p.search_toggle.click()
        p.search_input.send_keys("Hibana")
        assert "Hibana" in p.search_input.get_attribute("value")

    @allure.story("Search shows results")
    @allure.title("Результаты поиска")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_results(self, driver):
        p = load_page(driver)
        p.search_toggle.click()
        p.search_input.send_keys("Zanmu")
        time.sleep(2)
        assert p.search_results.is_visible()


@allure.epic("ADO Shop UI Tests")
@allure.feature("Collections")
class TestCollections:

    @allure.story("ALL MUSIC loads with products")
    @allure.title("ALL MUSIC")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_all_music(self, driver):
        load_page(driver, "collections/all")
        grid = driver.find_elements(By.ID, "product-grid")
        assert len(grid) > 0, "Product grid not found"

    @allure.story("Collection has product items")
    @allure.title("Товары в коллекции")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_has_products(self, driver):
        load_page(driver, "collections/all")
        items = driver.find_elements(By.CSS_SELECTOR, "#product-grid li.grid__item")
        assert len(items) > 0, f"Expected products, got {len(items)}"

    @allure.story("Hibana collection")
    @allure.title("Hibana")
    @allure.severity(allure.severity_level.NORMAL)
    def test_hibana(self, driver):
        load_page(driver, "collections/hibana")
        grid = driver.find_elements(By.ID, "product-grid")
        assert len(grid) > 0

    @allure.story("Zanmu collection")
    @allure.title("Zanmu")
    @allure.severity(allure.severity_level.NORMAL)
    def test_zanmu(self, driver):
        load_page(driver, "collections/2nd-original-album-zanmu")
        grid = driver.find_elements(By.ID, "product-grid")
        assert len(grid) > 0

    @allure.story("Phantom Siita collection")
    @allure.title("Phantom Siita")
    @allure.severity(allure.severity_level.NORMAL)
    def test_phantom_siita(self, driver):
        load_page(driver, "collections/phantom-siita")
        grid = driver.find_elements(By.ID, "product-grid")
        assert len(grid) > 0

    @allure.story("Merch collection")
    @allure.title("All Merch")
    @allure.severity(allure.severity_level.NORMAL)
    def test_all_merch(self, driver):
        load_page(driver, "collections/all-merch")
        grid = driver.find_elements(By.ID, "product-grid")
        assert len(grid) > 0


@allure.epic("ADO Shop UI Tests")
@allure.feature("Product Pages")
class TestProducts:

    def _open_first_product(self, driver):
        load_page(driver, "collections/all")
        items = driver.find_elements(By.CSS_SELECTOR, "#product-grid li.grid__item a[href*='/products/']")
        assert len(items) > 0
        href = items[0].get_attribute("href")
        driver.get(href)
        time.sleep(3)

    @allure.story("Product has title and price")
    @allure.title("Заголовок и цена")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_title_and_price(self, driver):
        self._open_first_product(driver)
        h1 = driver.find_elements(By.TAG_NAME, "h1")
        assert len(h1) > 0 and h1[0].text, "Product title missing"
        price = driver.find_elements(By.CSS_SELECTOR, ".price-item--regular")
        assert len(price) > 0, "Product price missing"

    @allure.story("Product has description")
    @allure.title("Описание")
    @allure.severity(allure.severity_level.NORMAL)
    def test_description(self, driver):
        self._open_first_product(driver)
        desc = driver.find_elements(By.CSS_SELECTOR, ".product__description")
        assert len(desc) > 0

    @allure.story("Product has image")
    @allure.title("Изображение")
    @allure.severity(allure.severity_level.NORMAL)
    def test_image(self, driver):
        self._open_first_product(driver)
        img = driver.find_elements(By.CSS_SELECTOR, ".product__media img")
        assert len(img) > 0

    @allure.story("Product has Add to Cart or Sold out button")
    @allure.title("Кнопка")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_button(self, driver):
        self._open_first_product(driver)
        btn = driver.find_elements(By.CSS_SELECTOR, 'button[name="add"]')
        assert len(btn) > 0


@allure.epic("ADO Shop UI Tests")
@allure.feature("Cart")
class TestCart:

    @allure.story("Empty cart shows message")
    @allure.title("Пустая корзина")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_empty_cart(self, driver):
        load_page(driver, "cart")
        assert "/cart" in driver.current_url
        msgs = driver.find_elements(By.XPATH, "//*[contains(text(),'Your cart is empty')]")
        assert len(msgs) > 0

    @allure.story("Checkout button present")
    @allure.title("Кнопка Checkout")
    @allure.severity(allure.severity_level.NORMAL)
    def test_checkout(self, driver):
        load_page(driver, "cart")
        btn = driver.find_elements(By.CSS_SELECTOR, 'button[name="checkout"]')
        assert len(btn) > 0


@allure.epic("ADO Shop UI Tests")
@allure.feature("Footer")
class TestFooter:

    @allure.story("Footer visible")
    @allure.title("Футер виден")
    @allure.severity(allure.severity_level.NORMAL)
    def test_footer_visible(self, driver):
        p = load_page(driver)
        p.scroll_down()
        assert p.footer_element.is_visible()

    @allure.story("Social links present")
    @allure.title("Соцсети")
    @allure.severity(allure.severity_level.NORMAL)
    def test_social(self, driver):
        p = load_page(driver)
        p.scroll_down()
        assert p.footer_instagram.is_visible()
        assert p.footer_twitter.is_visible()
        assert p.footer_facebook.is_visible()
        assert p.footer_youtube.is_visible()

    @allure.story("Policy links present")
    @allure.title("Ссылки политик")
    @allure.severity(allure.severity_level.NORMAL)
    def test_policies(self, driver):
        p = load_page(driver)
        p.scroll_down()
        assert p.footer_privacy_policy.is_visible()
        assert p.footer_refund_policy.is_visible()
        assert p.footer_terms_of_service.is_visible()
        assert p.footer_legal_notice.is_visible()

    @allure.story("Privacy Policy loads")
    @allure.title("Privacy Policy")
    @allure.severity(allure.severity_level.NORMAL)
    def test_privacy(self, driver):
        load_page(driver, "policies/privacy-policy")
        assert "/policies/privacy-policy" in driver.current_url

    @allure.story("Refund Policy loads")
    @allure.title("Refund Policy")
    @allure.severity(allure.severity_level.NORMAL)
    def test_refund(self, driver):
        load_page(driver, "policies/refund-policy")
        assert "/policies/refund-policy" in driver.current_url

    @allure.story("Terms of Service loads")
    @allure.title("Terms of Service")
    @allure.severity(allure.severity_level.NORMAL)
    def test_terms(self, driver):
        load_page(driver, "policies/terms-of-service")
        assert "/policies/terms-of-service" in driver.current_url


@allure.epic("ADO Shop UI Tests")
@allure.feature("Homepage")
class TestHomepage:

    @allure.story("Main content visible")
    @allure.title("Главный контент")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_main_content(self, driver):
        p = load_page(driver)
        mc = driver.find_elements(By.ID, "MainContent")
        assert len(mc) > 0

    @allure.story("Page title contains Ado")
    @allure.title("Заголовок страницы")
    @allure.severity(allure.severity_level.NORMAL)
    def test_title(self, driver):
        load_page(driver)
        title = driver.title
        assert "Ado" in title

    @allure.story("Images have src")
    @allure.title("Изображения")
    @allure.severity(allure.severity_level.MINOR)
    def test_images(self, driver):
        load_page(driver)
        imgs = driver.find_elements(By.TAG_NAME, "img")
        for img in imgs[:5]:
            assert img.get_attribute("src")


@allure.epic("ADO Shop UI Tests")
@allure.feature("Navigation Flows")
class TestFlows:

    @allure.story("Collection -> product -> back")
    @allure.title("Полный путь")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_full_flow(self, driver):
        load_page(driver, "collections/hibana")
        grid = driver.find_elements(By.ID, "product-grid")
        assert len(grid) > 0
        items = driver.find_elements(By.CSS_SELECTOR, "#product-grid li.grid__item a[href*='/products/']")
        assert len(items) > 0
        href = items[0].get_attribute("href")
        driver.get(href)
        time.sleep(3)
        h1 = driver.find_elements(By.TAG_NAME, "h1")
        assert len(h1) > 0
        driver.back()
        time.sleep(2)
        assert "hibana" in driver.current_url

    @allure.story("Multiple collections via URL")
    @allure.title("Несколько коллекций")
    @allure.severity(allure.severity_level.NORMAL)
    def test_multi_collection(self, driver):
        load_page(driver, "collections/hibana")
        assert "hibana" in driver.current_url
        load_page(driver, "collections/2nd-original-album-zanmu")
        assert "zanmu" in driver.current_url
        load_page(driver, "collections/phantom-siita")
        assert "phantom-siita" in driver.current_url

    @allure.story("Search opens and accepts input")
    @allure.title("Поиск")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search(self, driver):
        p = load_page(driver)
        p.search_toggle.click()
        assert p.search_input.is_visible()
        p.search_input.send_keys("Hibana")
        time.sleep(2)
        assert p.search_results.is_visible()
