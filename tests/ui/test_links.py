import time
import pytest
import allure
import requests
from helpers.config import BASE_URL


INTERNAL_URLS = [
    # Collections
    ("/collections/all", "ALL MUSIC"),
    ("/collections/hibana", "Hibana"),
    ("/collections/2nd-original-album-zanmu", "Zanmu"),
    ("/collections/phantom-siita", "Phantom Siita"),
    ("/collections/phantom-siita-love-hate", "Phantom Siita Love Hate"),
    ("/collections/phantom-siita-merch", "Phantom Siita Merch"),
    ("/collections/horror-queen", "Horror Queen"),
    ("/collections/vivarium", "Vivarium"),
    ("/collections/yodaka", "Yodaka"),
    ("/collections/shinzou", "Shinzou"),
    ("/collections/ados-best-adobum", "Ado's Best Adobum"),
    ("/collections/ados-best-adobum-vinyl", "Ado's Best Adobum Vinyl"),
    ("/collections/profile_of_mona_lisa", "Profile of Mona Lisa"),
    ("/collections/crunchyroll-goods", "Crunchyroll Goods"),
    ("/collections/all-merch", "All Merch"),
    ("/collections/sakura-biyori-and-time-machine-with-hatsune-miku-shoka", "Sakura Biyori"),
    ("/collections/ado-official-calendar-2025", "Ado Calendar 2025"),
    # Products
    ("/products/tyjt59005", "Ado 3rd Vinyl Record"),
    ("/products/tybt19055", "Yodaka Limited Vinyl"),
    ("/products/tyxt19046", "Yodaka Limited CD"),
    ("/products/tyxt10091", "Yodaka Standard CD"),
    ("/products/tybt10102", "Yodaka Standard Vinyl"),
    ("/products/d2jl1001", "Vivarium Limited Box"),
    ("/products/tykt59001", "Vivarium Limited Vinyl"),
    ("/products/pdcv5090", "Horror Queen Limited"),
    ("/products/d2cl1001", "Horror Queen 3-Version"),
    ("/products/tyct39329", "Horror Queen Limited CD"),
    ("/products/tyct39330", "Horror Queen Limited CD 2"),
    ("/products/tyct39343", "Horror Queen Standard CD"),
    ("/products/tyjt59012", "Ado's Best Adobum Vinyl 1"),
    ("/products/tyjt59014", "Ado's Best Adobum Vinyl 2"),
    ("/products/pdcv1247", "Ado's Best Adobum Limited 1"),
    ("/products/pdcv1248", "Ado's Best Adobum Limited 2"),
    ("/products/tyct69342", "Ado's Best Adobum CD 1"),
    ("/products/tyct69343", "Ado's Best Adobum CD 2"),
    ("/products/tyct69344", "Ado's Best Adobum CD 3"),
    ("/products/tyct69345", "Ado's Best Adobum CD 4"),
    ("/products/tyct60245", "Ado's Best Adobum CD 5"),
    # Pages
    ("/pages/help", "Help"),
    ("/pages/contact", "Contact"),
    ("/pages/notice-getting-your-order-right", "Notice Order"),
    ("/pages/notice-on-cancellation-of-orders", "Notice Cancellation"),
    # Policies
    ("/policies/privacy-policy", "Privacy Policy"),
    ("/policies/refund-policy", "Refund Policy"),
    ("/policies/terms-of-service", "Terms of Service"),
    ("/policies/legal-notice", "Legal Notice"),
    # Cart
    ("/cart", "Cart"),
    # Home
    ("/", "Home"),
]


@allure.epic("ADO Shop Link Check")
@allure.feature("Internal Links")
class TestInternalLinks:

    @allure.story("All internal links return 200")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize("path,label", INTERNAL_URLS, ids=[u[0] for u in INTERNAL_URLS])
    def test_link_returns_200(self, path, label):
        url = f"{BASE_URL}{path}"
        response = requests.get(url, timeout=15, allow_redirects=True)
        assert response.status_code == 200, (
            f"{label} ({path}) returned {response.status_code}"
        )

    @allure.story("Social links return 200")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("url,label", [
        ("https://www.instagram.com/ado_staff_official/", "Instagram"),
        ("https://twitter.com/ado1024imokenp", "Twitter"),
        ("https://www.facebook.com/ado1024.official/", "Facebook"),
        ("https://www.youtube.com/@Ado1024", "YouTube"),
    ])
    def test_social_link_returns_200(self, url, label):
        response = requests.get(url, timeout=15, allow_redirects=True)
        assert response.status_code == 200, (
            f"{label} ({url}) returned {response.status_code}"
        )
