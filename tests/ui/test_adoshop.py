import time

from selenium.common import NoSuchElementException

from conftest import driver
from locators.main_locators import WebPage, MainPage
from conftest import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def test_ado_shop(driver):
    page = MainPage(driver)
    # page.head_btn_main.get_attribute(attr_name=)
    page.head_btn_country.get_text()


# def is_element_in_header(driver, css_selector):
#     try:
#         # Ищем элемент, находящийся именно внутри header
#         header = driver.find_element(By.TAG_NAME, 'header')
#         header.find_element(By.CSS_SELECTOR, css_selector)
#         return True
#     except NoSuchElementException:
#         return False
#
#
# def is_element_in_footer(driver, css_selector):
#     try:
#         # Ищем элемент, находящийся именно внутри footer
#         footer = driver.find_element(By.TAG_NAME, 'footer')
#         footer.find_element(By.CSS_SELECTOR, css_selector)
#         return True
#     except NoSuchElementException:
#         return False


# Инициализируем ожидание до 10 секунд
wait = WebDriverWait(driver, 10)

try:
    # 1. Проверяем, что сам хедер отображается на странице
    header = wait.until(EC.visibility_of_element_located((By.TAG_NAME, "header")))
    print("Хедер успешно отображается на странице.")

    # 2. Ищем элементы внутри найденного хедера (Относительный поиск)
    # Проверка логотипа
    logo = header.find_element(By.CSS_SELECTOR, ".logo-img") # замените класс на свой
    assert logo.is_displayed(), "Логотип в хедере не отображается"

    # Проверка ссылки на личный кабинет
    profile_link = header.find_element(By.XPATH, ".//a[contains(@href, '/profile')]")
    assert profile_link.is_enabled(), "Ссылка на профиль заблокирована"

    print("Все базовые элементы хедера успешно проверены!")

except TimeoutException:
    print("Ошибка: Хедер или ключевые элементы не загрузились вовремя.")
except AssertionError as error:
    print(f"Ошибка проверки элемента: {error}")
finally:
    driver.quit()

# class MainPage (WebPage):
#     def __init__(self, webdriver):
