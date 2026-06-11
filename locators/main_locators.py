import os
from pages.elements import WebElement, ManyWebElements
from pages.base_page import WebPage


class MainPage(WebPage):
    def __init__(self, web_driver, url=''):
        if not url:
            url = os.getenv("MAIN_PAGE") or 'https://ado-shop.com/'

            super().__init__(web_driver, url)

    head_btn_main = WebElement(xpath='//*[@aria-controls="HeaderCountry-country-results"]//span')
    head_btn_home = WebElement(xpath='(//*[@aria-current="page"])[2]//span')
    head_btn_music = WebElement(xpath='(//*[@aria-expanded="false"])[6]//span')
    head_btn_merch = WebElement(xpath='(//*[@aria-expanded="false"])[7]//span')
    head_btn_help = WebElement(xpath='//*[@id="HeaderMenu-help"]//span')
    head_btn_contact = WebElement(xpath='//*[@id="HeaderMenu-contact"]//span')
    head_btn_language = WebElement(xpath='//*[@aria-controls="HeaderLanguageList"]//span')
    head_btn_country = WebElement(xpath='//*[@aria-controls="HeaderCountry-country-results"]//span')
    head_btn_search = WebElement(xpath='(//*[@aria-haspopup="dialog"]//*[@aria-hidden="true"])[1]')
    head_btn_profile = WebElement(ID='cart-icon-bubble')
    head_btn_cart = WebElement(xpath='//*[@id="cart-icon-bubble"]//*[@aria-hidden="true"]')
