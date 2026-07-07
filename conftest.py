"""
Модуль конфигурации тестов (conftest).

Содержит фикстуры для настройки WebDriver браузера Chrome,
используемые в тестах проекта ADOsite.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import allure
from helpers.config import BASE_URL


@pytest.fixture(scope="session")
def driver():
    """
    Фикстура для создания и настройки WebDriver браузера Chrome.

    Один браузер на всю сессию тестов (scope="session").
    Между тестами возвращается на главную страницу.

    Yields:
        webdriver.Chrome: экземпляр WebDriver для взаимодействия с браузером.
    """
    chrome_options = Options()
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)

    yield driver

    driver.quit()


@pytest.fixture(autouse=True)
def _reset_page(driver):
    """Переход на главную после каждого теста."""
    yield
    driver.get(BASE_URL)
