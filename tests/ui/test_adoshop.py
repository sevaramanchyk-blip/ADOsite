"""Базовые UI-тесты элементов сайта ado-shop.com."""
from core.locators.main_locators import MainPage
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from helpers.config import MAIN_URL


def test_ado_shop(driver):
    """Проверка базовой загрузки страницы через Page Object."""
    page = MainPage(driver)
    page.head_btn_country.get_text()


def test_header_elements(driver):
    """Проверка наличия логотипа и ссылки на профиль в хедере."""
    driver.get(MAIN_URL)
    wait = WebDriverWait(driver, 10)

    # Ждём загрузки хедера
    header = wait.until(
        EC.visibility_of_element_located((By.TAG_NAME, "header"))
    )

    # Проверяем логотип
    logo = header.find_element(By.CSS_SELECTOR, ".header__heading-logo")
    assert logo.is_displayed(), "Логотип в хедере не отображается"

    # Проверяем ссылку на профиль
    account_link = header.find_element(
        By.CSS_SELECTOR,
        ".header__icon--account"
    )
    assert account_link.is_enabled(), "Ссылка на профиль заблокирована"
