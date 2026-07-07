import os
from core.pages.elements import WebElement, ManyWebElements
from core.pages.base_page import WebPage
from helpers.config import MAIN_URL, BASE_URL


class MainPage(WebPage):
    def __init__(self, web_driver, url=''):
        if not url:
            url = os.getenv("MAIN_PAGE") or MAIN_URL

            super().__init__(web_driver, url)

    # ======================== HEADER ========================

    header_element = WebElement(
        xpath='//header'
    )
    header_logo = WebElement(
        xpath='//header//a[@class*="header__heading-link"]'
    )
    nav_links = ManyWebElements(
        xpath='//header//a[contains(@class, "header__menu-item")]'
    )
    cart_link = WebElement(
        xpath='//a[contains(@class, "header__icon--cart")]'
    )

    # ======================== SEARCH ========================

    search_toggle = WebElement(
        xpath='//details-modal[@class="header__search"]'
              '//summary[contains(@class, "header__icon--search")]'
    )
    search_input = WebElement(
        xpath='//predictive-search//input[@type="search"]'
    )
    search_results = WebElement(
        xpath='//predictive-search//*[@id="predictive-search-results"]'
    )

    # ======================== COLLECTION PAGE ========================

    collection_product_grid = WebElement(
        xpath='//*[@id="product-grid"]'
    )
    collection_product_items = ManyWebElements(
        xpath='//*[@id="product-grid"]//li[contains(@class, "grid__item")]'
    )
    product_title_links = ManyWebElements(
        xpath='//a[contains(@class, "full-unstyled-link")]'
    )

    # ======================== PRODUCT PAGE ========================

    product_title = WebElement(
        xpath='//h1'
    )
    product_price = WebElement(
        xpath='//span[contains(@class, "price-item--regular")]'
    )
    product_add_to_cart = WebElement(
        xpath='//button[@name="add"]'
    )
    product_description = WebElement(
        xpath='//div[contains(@class, "product__description")]'
    )
    product_image = WebElement(
        xpath='//div[contains(@class, "product__media")]//img'
    )

    # ======================== CART PAGE ========================

    cart_page_heading = WebElement(
        xpath='//h1'
    )
    cart_empty_message = WebElement(
        xpath='//*[contains(text(), "Your cart is empty")]'
    )
    checkout_button = WebElement(
        xpath='//button[@name="checkout"]'
    )

    # ======================== FOOTER ========================

    footer_element = WebElement(
        xpath='//footer'
    )
    footer_instagram = WebElement(
        xpath='//footer//a[contains(@href, "instagram.com")]'
    )
    footer_twitter = WebElement(
        xpath='//footer//a[contains(@href, "twitter.com")]'
    )
    footer_facebook = WebElement(
        xpath='//footer//a[contains(@href, "facebook.com")]'
    )
    footer_youtube = WebElement(
        xpath='//footer//a[contains(@href, "youtube.com")]'
    )
    footer_privacy_policy = WebElement(
        xpath='//footer//a[@href="/policies/privacy-policy"]'
    )
    footer_refund_policy = WebElement(
        xpath='//footer//a[@href="/policies/refund-policy"]'
    )
    footer_terms_of_service = WebElement(
        xpath='//footer//a[@href="/policies/terms-of-service"]'
    )
    footer_legal_notice = WebElement(
        xpath='//footer//a[@href="/policies/legal-notice"]'
    )

    # ======================== GENERIC ========================

    main_content = WebElement(
        xpath='//*[@id="MainContent"]'
    )
    h1_title = WebElement(
        xpath='//h1'
    )
    page_title = WebElement(
        xpath='//title'
    )
    all_images = ManyWebElements(
        xpath='//img'
    )
    all_links = ManyWebElements(
        xpath='//a'
    )

    # ======================== COLLECTION URLS ========================

    @staticmethod
    def collection_url(slug):
        return f"{BASE_URL}/collections/{slug}"

    COLLECTIONS = {
        'all': 'collections/all',
        'hibana': 'collections/hibana',
        'zanmu': 'collections/2nd-original-album-zanmu',
        'shinzou': 'collections/shinzou',
        'yodaka': 'collections/yodaka',
        'vivarium': 'collections/vivarium',
        'best_adobum': 'collections/ados-best-adobum',
        'phantom_siita': 'collections/phantom-siita',
        'horror_queen': 'collections/horror-queen',
        'mona_lisa': 'collections/profile_of_mona_lisa',
        'crunchyroll': 'collections/crunchyroll-goods',
        'all_merch': 'collections/all-merch',
        'calendar': 'collections/ado-official-calendar-2025',
    }
