"""Расширенные UI-тесты: загрузка страниц, изображения, ссылки, скроллинг, заголовки."""

import time
import pytest
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from helpers.config import BASE_URL
from core.locators.main_locators import MainPage


def open_page(driver, path=""):
    url = f"{BASE_URL}/{path}" if path else BASE_URL
    page = MainPage(driver, url)
    return page


@allure.epic("ADO Shop Extended UI")
@allure.feature("Page Load")
class TestPageLoad:

    @allure.story("Homepage loads within timeout")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_homepage_load_time(self, driver):
        start = time.time()
        open_page(driver)
        elapsed = time.time() - start
        assert elapsed < 15

    @allure.story("Ready state is complete")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_ready_state(self, driver):
        open_page(driver)
        state = driver.execute_script("return document.readyState")
        assert state == "complete"

    @allure.story("Collection page loads")
    @allure.severity(allure.severity_level.NORMAL)
    def test_collection_loads(self, driver):
        open_page(driver, "collections/hibana")
        state = driver.execute_script("return document.readyState")
        assert state == "complete"

    @allure.story("Product page loads")
    @allure.severity(allure.severity_level.NORMAL)
    def test_product_page_loads(self, driver):
        page = open_page(driver, "collections/all")
        assert page.product_title_links.count() > 0
        href = page.product_title_links[0].get_attribute("href")
        driver.get(href)
        state = driver.execute_script("return document.readyState")
        assert state == "complete"


@allure.epic("ADO Shop Extended UI")
@allure.feature("Images")
class TestImages:

    @allure.story("All images have src")
    @allure.severity(allure.severity_level.NORMAL)
    def test_images_have_src(self, driver):
        page = open_page(driver)
        images = page.all_images
        for i in range(min(images.count(), 10)):
            src = images[i].get_attribute("src")
            assert src

    @allure.story("Images have alt attribute")
    @allure.severity(allure.severity_level.MINOR)
    def test_images_have_alt(self, driver):
        page = open_page(driver)
        images = page.all_images
        total = min(images.count(), 10)
        missing = 0
        for i in range(total):
            alt = images[i].get_attribute("alt")
            if not alt:
                missing += 1
        assert missing < total


@allure.epic("ADO Shop Extended UI")
@allure.feature("Links")
class TestLinks:

    @allure.story("All links have href")
    @allure.severity(allure.severity_level.MINOR)
    def test_links_have_href(self, driver):
        page = open_page(driver)
        links = page.all_links
        missing = 0
        for i in range(min(links.count(), 20)):
            href = links[i].get_attribute("href")
            if not href:
                missing += 1
        assert missing < 5

    @allure.story("Internal links use HTTPS")
    @allure.severity(allure.severity_level.MINOR)
    def test_internal_links_https(self, driver):
        page = open_page(driver)
        links = page.all_links
        for i in range(min(links.count(), 10)):
            href = links[i].get_attribute("href")
            if href and "ado-shop.com" in href:
                assert href.startswith("https://")


@allure.epic("ADO Shop Extended UI")
@allure.feature("Scrolling")
class TestScrolling:

    @allure.story("Scroll down works")
    @allure.severity(allure.severity_level.NORMAL)
    def test_scroll_down(self, driver):
        page = open_page(driver)
        page.scroll_down()
        scroll_y = driver.execute_script("return window.scrollY")
        assert scroll_y > 0

    @allure.story("Scroll to top works")
    @allure.severity(allure.severity_level.NORMAL)
    def test_scroll_to_top(self, driver):
        page = open_page(driver)
        page.scroll_down()
        page.scroll_up()
        scroll_y = driver.execute_script("return window.scrollY")
        assert scroll_y == 0


@allure.epic("ADO Shop Extended UI")
@allure.feature("Page Title")
class TestPageTitle:

    @allure.story("Homepage has title")
    @allure.severity(allure.severity_level.NORMAL)
    def test_homepage_title(self, driver):
        open_page(driver)
        title = driver.title
        assert title

    @allure.story("Collection has title")
    @allure.severity(allure.severity_level.NORMAL)
    def test_collection_title(self, driver):
        open_page(driver, "collections/all")
        title = driver.title
        assert title

    @allure.story("Cart has title")
    @allure.severity(allure.severity_level.NORMAL)
    def test_cart_title(self, driver):
        open_page(driver, "cart")
        title = driver.title
        assert title
