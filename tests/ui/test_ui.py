"""Основные UI-тесты: хедер, поиск, коллекции, товары, корзина, футер, навигация."""

import pytest
import allure
from selenium.webdriver.common.by import By
from helpers.config import BASE_URL
from core.locators.main_locators import MainPage


def open_page(driver, path=""):
    url = f"{BASE_URL}/{path}" if path else BASE_URL
    page = MainPage(driver, url)
    return page


@allure.epic("ADO Shop UI Tests")
@allure.feature("Header Navigation")
class TestHeader:

    @allure.story("Header is visible")
    @allure.title("Проверка хедера")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_header_visible(self, driver):
        page = open_page(driver)
        assert page.header_element.is_visible()

    @allure.story("Navigation links present")
    @allure.title("Ссылки навигации")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_nav_links(self, driver):
        page = open_page(driver)
        assert page.nav_links.count() >= 5

    @allure.story("Cart link present")
    @allure.title("Ссылка корзины")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_cart_link(self, driver):
        page = open_page(driver)
        assert page.cart_link.is_visible()

    @allure.story("Cart navigates to /cart")
    @allure.title("Переход в корзину")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_cart_navigates(self, driver):
        page = open_page(driver)
        page.cart_link.click()
        assert "/cart" in driver.current_url


@allure.epic("ADO Shop UI Tests")
@allure.feature("Search")
class TestSearch:

    @allure.story("Search opens input")
    @allure.title("Открытие поиска")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_opens(self, driver):
        page = open_page(driver)
        page.search_toggle.click()
        assert page.search_input.is_visible()

    @allure.story("Search accepts text")
    @allure.title("Ввод текста")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_text(self, driver):
        page = open_page(driver)
        page.search_toggle.click()
        page.search_input.send_keys("Hibana")
        assert "Hibana" in page.search_input.get_attribute("value")

    @allure.story("Search shows results")
    @allure.title("Результаты поиска")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_results(self, driver):
        page = open_page(driver)
        page.search_toggle.click()
        page.search_input.send_keys("Zanmu")
        assert page.search_results.is_visible()


@allure.epic("ADO Shop UI Tests")
@allure.feature("Collections")
class TestCollections:

    @allure.story("ALL MUSIC loads with products")
    @allure.title("ALL MUSIC")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_all_music(self, driver):
        page = open_page(driver, "collections/all")
        assert page.collection_product_grid.is_visible()

    @allure.story("Collection has product items")
    @allure.title("Товары в коллекции")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_has_products(self, driver):
        page = open_page(driver, "collections/all")
        assert page.collection_product_items.count() > 0

    @allure.story("Hibana collection")
    @allure.title("Hibana")
    @allure.severity(allure.severity_level.NORMAL)
    def test_hibana(self, driver):
        page = open_page(driver, "collections/hibana")
        assert page.collection_product_grid.is_visible()

    @allure.story("Zanmu collection")
    @allure.title("Zanmu")
    @allure.severity(allure.severity_level.NORMAL)
    def test_zanmu(self, driver):
        page = open_page(driver, "collections/2nd-original-album-zanmu")
        assert page.collection_product_grid.is_visible()

    @allure.story("Phantom Siita collection")
    @allure.title("Phantom Siita")
    @allure.severity(allure.severity_level.NORMAL)
    def test_phantom_siita(self, driver):
        page = open_page(driver, "collections/phantom-siita")
        assert page.collection_product_grid.is_visible()

    @allure.story("Merch collection")
    @allure.title("All Merch")
    @allure.severity(allure.severity_level.NORMAL)
    def test_all_merch(self, driver):
        page = open_page(driver, "collections/all-merch")
        assert page.collection_product_grid.is_visible()


@allure.epic("ADO Shop UI Tests")
@allure.feature("Product Pages")
class TestProducts:

    def _open_first_product(self, driver):
        page = open_page(driver, "collections/all")
        assert page.collection_product_items.count() > 0
        product_link = page.product_title_links[0]
        href = product_link.get_attribute("href")
        driver.get(href)

    @allure.story("Product has title and price")
    @allure.title("Заголовок и цена")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_title_and_price(self, driver):
        self._open_first_product(driver)
        page = MainPage(driver)
        assert page.product_title.get_text(), "Product title missing"
        assert page.product_price.is_visible(), "Product price missing"

    @allure.story("Product has description")
    @allure.title("Описание")
    @allure.severity(allure.severity_level.NORMAL)
    def test_description(self, driver):
        self._open_first_product(driver)
        page = MainPage(driver)
        assert page.product_description.is_visible()

    @allure.story("Product has image")
    @allure.title("Изображение")
    @allure.severity(allure.severity_level.NORMAL)
    def test_image(self, driver):
        self._open_first_product(driver)
        page = MainPage(driver)
        assert page.product_image.is_visible()

    @allure.story("Product has Add to Cart or Sold out button")
    @allure.title("Кнопка")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_button(self, driver):
        self._open_first_product(driver)
        page = MainPage(driver)
        assert page.product_add_to_cart.is_visible()


@allure.epic("ADO Shop UI Tests")
@allure.feature("Cart")
class TestCart:

    @allure.story("Empty cart shows message")
    @allure.title("Пустая корзина")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_empty_cart(self, driver):
        page = open_page(driver, "cart")
        assert "/cart" in driver.current_url
        assert page.cart_empty_message.is_visible()

    @allure.story("Checkout button present")
    @allure.title("Кнопка Checkout")
    @allure.severity(allure.severity_level.NORMAL)
    def test_checkout(self, driver):
        page = open_page(driver, "cart")
        assert page.checkout_button.is_visible()


@allure.epic("ADO Shop UI Tests")
@allure.feature("Footer")
class TestFooter:

    @allure.story("Footer visible")
    @allure.title("Футер виден")
    @allure.severity(allure.severity_level.NORMAL)
    def test_footer_visible(self, driver):
        page = open_page(driver)
        page.scroll_down()
        assert page.footer_element.is_visible()

    @allure.story("Social links present")
    @allure.title("Соцсети")
    @allure.severity(allure.severity_level.NORMAL)
    def test_social(self, driver):
        page = open_page(driver)
        page.scroll_down()
        assert page.footer_instagram.is_visible()
        assert page.footer_twitter.is_visible()
        assert page.footer_facebook.is_visible()
        assert page.footer_youtube.is_visible()

    @allure.story("Policy links present")
    @allure.title("Ссылки политик")
    @allure.severity(allure.severity_level.NORMAL)
    def test_policies(self, driver):
        page = open_page(driver)
        page.scroll_down()
        assert page.footer_privacy_policy.is_visible()
        assert page.footer_refund_policy.is_visible()
        assert page.footer_terms_of_service.is_visible()
        assert page.footer_legal_notice.is_visible()

    @allure.story("Privacy Policy loads")
    @allure.title("Privacy Policy")
    @allure.severity(allure.severity_level.NORMAL)
    def test_privacy(self, driver):
        page = open_page(driver, "policies/privacy-policy")
        assert "/policies/privacy-policy" in driver.current_url

    @allure.story("Refund Policy loads")
    @allure.title("Refund Policy")
    @allure.severity(allure.severity_level.NORMAL)
    def test_refund(self, driver):
        page = open_page(driver, "policies/refund-policy")
        assert "/policies/refund-policy" in driver.current_url

    @allure.story("Terms of Service loads")
    @allure.title("Terms of Service")
    @allure.severity(allure.severity_level.NORMAL)
    def test_terms(self, driver):
        page = open_page(driver, "policies/terms-of-service")
        assert "/policies/terms-of-service" in driver.current_url


@allure.epic("ADO Shop UI Tests")
@allure.feature("Homepage")
class TestHomepage:

    @allure.story("Main content visible")
    @allure.title("Главный контент")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_main_content(self, driver):
        page = open_page(driver)
        assert page.main_content.is_visible()

    @allure.story("Page title contains Ado")
    @allure.title("Заголовок страницы")
    @allure.severity(allure.severity_level.NORMAL)
    def test_title(self, driver):
        page = open_page(driver)
        title = driver.title
        assert "Ado" in title

    @allure.story("Images have src")
    @allure.title("Изображения")
    @allure.severity(allure.severity_level.MINOR)
    def test_images(self, driver):
        page = open_page(driver)
        images = page.all_images
        for i in range(min(images.count(), 5)):
            assert images[i].get_attribute("src")


@allure.epic("ADO Shop UI Tests")
@allure.feature("Navigation Flows")
class TestFlows:

    @allure.story("Collection -> product -> back")
    @allure.title("Полный путь")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_full_flow(self, driver):
        page = open_page(driver, "collections/hibana")
        assert page.collection_product_grid.is_visible()
        assert page.collection_product_items.count() > 0
        product_link = page.product_title_links[0]
        href = product_link.get_attribute("href")
        driver.get(href)
        product_page = MainPage(driver)
        assert product_page.product_title.get_text()
        driver.back()
        assert "hibana" in driver.current_url

    @allure.story("Multiple collections via URL")
    @allure.title("Несколько коллекций")
    @allure.severity(allure.severity_level.NORMAL)
    def test_multi_collection(self, driver):
        page = open_page(driver, "collections/hibana")
        assert "hibana" in driver.current_url
        page = open_page(driver, "collections/2nd-original-album-zanmu")
        assert "zanmu" in driver.current_url
        page = open_page(driver, "collections/phantom-siita")
        assert "phantom-siita" in driver.current_url

    @allure.story("Search opens and accepts input")
    @allure.title("Поиск")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search(self, driver):
        page = open_page(driver)
        page.search_toggle.click()
        assert page.search_input.is_visible()
        page.search_input.send_keys("Hibana")
        assert page.search_results.is_visible()
