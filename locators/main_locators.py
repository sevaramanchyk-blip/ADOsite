import os
from pages.elements import WebElement, ManyWebElements
from pages.base_page import WebPage


class MainPage(WebPage):
    def __init__(self, web_driver, url=''):
        if not url:
            url = os.getenv("MAIN_PAGE") or 'https://ado-shop.com/'

            super().__init__(web_driver, url)

    btn_ado = WebElement(xpath='<div class="header__heading-logo-wrapper"')
