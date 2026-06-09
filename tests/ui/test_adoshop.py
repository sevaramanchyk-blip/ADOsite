import time
from conftest import driver
from locators.main_locators import WebPage, MainPage


def test_ado_shop(driver):
    page = MainPage(driver)

    print(page.btn_ado).get_text

# class MainPage (WebPage):
#     def __init__(self, webdriver):
