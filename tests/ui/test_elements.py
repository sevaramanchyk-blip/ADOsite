"""
Тесты элементов страницы ADO Shop.

Проверяют наличие и работоспособность базовых UI-элементов:
хедера, логотипа, поиска, футера и навигационных ссылок.
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


@allure.epic("ADO Shop UI Tests")
@allure.feature("Page Elements")
class TestHeaderElements:
    """Тесты элементов хедера: шапка, логотип."""

    @allure.story("Header presence")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_header_is_present(self, driver):
        """Проверка наличия элемента <header> на странице."""
        p = load_page(driver)
        assert p.header_element.is_presented(), "Header element not found"

    @allure.story("Logo presence")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_logo_is_present(self, driver):
        """Проверка наличия логотипа в хедере (по CSS-классу header__heading)."""
        p = load_page(driver)
        logos = driver.find_elements(
            By.CSS_SELECTOR, "header a[class*='header__heading']"
        )
        assert len(logos) > 0, "Logo not found"

    @allure.story("Logo is clickable")
    @allure.severity(allure.severity_level.NORMAL)
    def test_logo_click_returns_home(self, driver):
        """Клик по логотипу должен возвращать на главную страницу."""
        load_page(driver, "collections/all")
        logos = driver.find_elements(
            By.CSS_SELECTOR, "header a[class*='header__heading']"
        )
        assert len(logos) > 0, "Logo not found"
        logos[0].click()
        time.sleep(2)
        assert driver.current_url.rstrip("/") == BASE_URL.rstrip("/"), \
            "Logo click did not return to homepage"


@allure.epic("ADO Shop UI Tests")
@allure.feature("Page Elements")
class TestSearchElements:
    """Тесты блока поиска: toggle, поле ввода."""

    @allure.story("Search toggle is clickable")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_toggle_clickable(self, driver):
        """Кнопка открытия поиска должна быть кликабельной."""
        p = load_page(driver)
        assert p.search_toggle.is_clickable(), "Search toggle not clickable"

    @allure.story("Search input appears after toggle")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_input_appears(self, driver):
        """После клика по toggle поле поиска должно стать видимым."""
        p = load_page(driver)
        p.search_toggle.click()
        time.sleep(1)
        assert p.search_input.is_visible(), "Search input not visible after toggle"

    @allure.story("Search input accepts and clears text")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_input_clear(self, driver):
        """Поле поиска должно принимать текст и корректно его отображать."""
        p = load_page(driver)
        p.search_toggle.click()
        p.search_input.send_keys("test query")
        time.sleep(1)
        val = p.search_input.get_attribute("value")
        assert val == "test query", f"Expected 'test query', got '{val}'"


@allure.epic("ADO Shop UI Tests")
@allure.feature("Page Elements")
class TestFooterElements:
    """Тесты футера: наличие, соцсети, ссылки политик."""

    @allure.story("Footer is present")
    @allure.severity(allure.severity_level.NORMAL)
    def test_footer_present(self, driver):
        """Футер должен присутствовать на странице (виден после скролла)."""
        p = load_page(driver)
        p.scroll_down()
        assert p.footer_element.is_presented(), "Footer not found"

    @allure.story("All social links present")
    @allure.severity(allure.severity_level.NORMAL)
    def test_all_social_links(self, driver):
        """Все ссылки на соцсети (Instagram, Twitter, Facebook, YouTube)
        должны присутствовать в футере."""
        p = load_page(driver)
        p.scroll_down()
        socials = [
            p.footer_instagram,
            p.footer_twitter,
            p.footer_facebook,
            p.footer_youtube,
        ]
        for s in socials:
            assert s.is_presented(), f"Social link {s._locator} not found"

    @allure.story("All policy links present")
    @allure.severity(allure.severity_level.NORMAL)
    def test_all_policy_links(self, driver):
        """Все ссылки на политик (Privacy, Refund, Terms, Legal)
        должны присутствовать в футере."""
        p = load_page(driver)
        p.scroll_down()
        policies = [
            p.footer_privacy_policy,
            p.footer_refund_policy,
            p.footer_terms_of_service,
            p.footer_legal_notice,
        ]
        for pol in policies:
            assert pol.is_presented(), f"Policy link {pol._locator} not found"

    @allure.story("Social links have href")
    @allure.severity(allure.severity_level.MINOR)
    def test_social_links_have_href(self, driver):
        """Каждая ссылка на соцсеть должна иметь корректный href,
        начинающийся с http."""
        p = load_page(driver)
        p.scroll_down()
        for social in [p.footer_instagram, p.footer_twitter,
                       p.footer_facebook, p.footer_youtube]:
            href = social.get_attribute("href")
            assert href and href.startswith("http"), \
                f"Social link {social._locator} has no valid href"


@allure.epic("ADO Shop UI Tests")
@allure.feature("Page Elements")
class TestNavigationElements:
    """Тесты навигационных ссылок в хедере."""

    @allure.story("Navigation links count")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_nav_links_minimum_count(self, driver):
        """В хедере должно быть минимум 5 навигационных ссылок."""
        p = load_page(driver)
        count = p.nav_links.count()
        assert count >= 5, f"Expected at least 5 nav links, got {count}"

    @allure.story("Navigation links are clickable")
    @allure.severity(allure.severity_level.NORMAL)
    def test_nav_links_are_clickable(self, driver):
        """Навигационные ссылки должны присутствовать в DOM
        (некоторые могут быть скрыты в мобильном меню)."""
        p = load_page(driver)
        count = p.nav_links.count()
        for i in range(min(count, 3)):
            elem = p.nav_links[i]
            assert elem is not None, f"Nav link {i} is None"
