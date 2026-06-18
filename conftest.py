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


@pytest.fixture
def driver():
    """
    Фикстура для создания и настройки WebDriver браузера Chrome.

    Запускает Chrome в режиме headless (без графического интерфейса)
    с максимальным размером окна. После завершения теста автоматически
    закрывает браузер.

    Yields:
        webdriver.Chrome: экземпляр WebDriver для взаимодействия с браузером.
    """
    # Настройка параметров запуска Chrome
    chrome_options = Options()
    chrome_options.add_argument('--start-maximized')  # Максимальный размер окна
    chrome_options.add_argument('--headless=new')  # Режим headless (без GUI)
    chrome_options.add_argument('--no-sandbox')  # Отключение песочницы (для CI/CD)
    chrome_options.add_argument('--disable-dev-shm-usage')  # Отключение использования /dev/shm

    # Инициализация WebDriver с настроенными параметрами
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)  # Неявное ожидание элементов до 10 секунд

    yield driver  # Передача управления тесту
    driver.quit()  # Закрытие браузера после завершения теста
