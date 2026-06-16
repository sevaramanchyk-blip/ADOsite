from locators.main_locators import MainPage
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


def test_ado_shop(driver):
    page = MainPage(driver)
    page.head_btn_country.get_text()


def test_header_elements(driver):
    driver.get('https://ado-shop.com/')
    wait = WebDriverWait(driver, 10)

    header = wait.until(
        EC.visibility_of_element_located((By.TAG_NAME, "header"))
    )

    logo = header.find_element(By.CSS_SELECTOR, ".header__heading-logo")
    assert logo.is_displayed(), "Логотип в хедере не отображается"

    account_link = header.find_element(
        By.CSS_SELECTOR,
        ".header__icon--account"
    )
    assert account_link.is_enabled(), "Ссылка на профиль заблокирована"
