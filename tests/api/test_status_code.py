"""Тесты API для проверки HTTP-ответов сайта ado-shop.com."""
import requests
import pytest
import allure

BASE_URL = "https://ado-shop.com"

COLLECTIONS = [
    ("shinzou", "Shinzou"),
    ("2nd-original-album-zanmu", "Zanmu"),
    ("hibana", "Hibana"),
    ("ados-best-adobum", "Ado's Best Adobum"),
    ("phantom-siita", "Phantom Siita"),
    ("all-merch", "All Merch"),
]


@allure.feature("Тесты api")
@allure.story("Проверка статус кода")
class TestApiStatusCodes:
    """Проверка HTTP-статус-кодов основных страниц."""
    @allure.title("Главная страница возвращает 200")
    def test_main_page_200(self):
        response = requests.get(BASE_URL)
        assert response.status_code == 200

    @allure.title("Несуществующая страница возвращает 404")
    def test_404_page(self):
        response = requests.get(f"{BASE_URL}/this-page-does-not-exist-12345")
        assert response.status_code == 404

    @allure.title("Коллекции возвращают 200")
    @pytest.mark.parametrize("slug,name", COLLECTIONS)
    def test_collections_200(self, slug, name):
        response = requests.get(f"{BASE_URL}/collections/{slug}")
        assert response.status_code == 200, (
            f"Коллекция {name} вернула {response.status_code}"
        )

    @allure.title("Редирект корзины на /cart")
    def test_cart_redirect(self):
        response = requests.get(
            f"{BASE_URL}/cart", allow_redirects=True
        )
        assert response.status_code == 200


@allure.feature("Тесты api")
@allure.story("Проверка времени отклика")
class TestApiPerformance:
    """Проверка времени отклика страниц."""
    @allure.title("Время отклика главной < 5 сек")
    def test_main_page_speed(self):
        response = requests.get(BASE_URL)
        assert response.elapsed.total_seconds() < 5, (
            f"Ответ за {response.elapsed.total_seconds():.2f} сек"
        )

    @allure.title("Время отклика коллекций < 5 сек")
    @pytest.mark.parametrize("slug,name", COLLECTIONS)
    def test_collection_speed(self, slug, name):
        response = requests.get(f"{BASE_URL}/collections/{slug}")
        assert response.elapsed.total_seconds() < 5, (
            f"{name}: {response.elapsed.total_seconds():.2f} сек"
        )


@allure.feature("Тесты api")
@allure.story("Проверка заголовков")
class TestApiHeaders:
    """Проверка HTTP-заголовков ответа."""
    @allure.title("Content-Type — text/html")
    def test_content_type(self):
        response = requests.get(BASE_URL)
        assert "text/html" in response.headers.get(
            "Content-Type", ""
        )

    @allure.title("Сервер отвечает Shopify")
    def test_server_shopify(self):
        response = requests.get(BASE_URL)
        server = response.headers.get("Server", "").lower()
        assert "cloudflare" in server or "shopify" in server, (
            f"Сервер: {server}"
        )

    @allure.title("Есть заголовок X-Content-Type-Options")
    def test_security_headers(self):
        response = requests.get(BASE_URL)
        assert "x-content-type-options" in {
            k.lower() for k in response.headers
        }


@allure.feature("Тесты api")
@allure.story("Проверка контента")
class TestApiContent:
    """Проверка контента страниц."""
    @allure.title("Главная содержит 'Ado'")
    def test_main_contains_ado(self):
        response = requests.get(BASE_URL)
        assert "ado" in response.text.lower()

    @allure.title("Главная содержит навигацию")
    def test_main_has_nav(self):
        response = requests.get(BASE_URL)
        assert "header" in response.text.lower()

    @allure.title("Коллекции содержат товары")
    @pytest.mark.parametrize("slug,name", COLLECTIONS[:3])
    def test_collections_have_products(self, slug, name):
        response = requests.get(f"{BASE_URL}/collections/{slug}")
        assert "product" in response.text.lower(), (
            f"Нет товаров в {name}"
        )

    @allure.title("JSON API — products endpoint")
    def test_products_json(self):
        response = requests.get(f"{BASE_URL}/products.json")
        assert response.status_code == 200
        data = response.json()
        assert "products" in data
        assert len(data["products"]) > 0
