import allure
from selenium.webdriver.common.by import By


def test_links5(driver):
    driver.get('https://ado-shop.com/')
    elements = [
        (driver.find_element(By.ID, "HeaderMenu-home"), 'Кнопка Home'),
        (driver.find_element(By.ID, "HeaderMenu-music"), 'Кнопка Music'),
        (driver.find_element(By.ID, "HeaderMenu-merch"), 'Кнопка Merch'),
        (driver.find_element(By.ID, "HeaderMenu-help"), 'Кнопка Help'),
        (driver.find_element(By.ID, "HeaderMenu-contact"), 'Кнопка Contact')
    ]
    for element, text_element in elements:
        with allure.step(f'Проверка кликабельно {text_element}'):
            assert element.is_enabled(), f'{text_element} не кликабельна'
