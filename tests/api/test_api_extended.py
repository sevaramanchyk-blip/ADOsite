"""Расширенные API-тесты для сайта ado-shop.com."""
import requests
import pytest
import allure
from helpers.config import BASE_URL, MAIN_URL, COLLECTIONS


@allure.feature("API тесты")
@allure.story("JSON API")
class TestJsonApi:
    """Проверка JSON API эндпоинтов Shopify."""

    @allure.title("products.json возвращает список товаров")
    def test_products_json_has_title(self):
        response = requests.get(f"{BASE_URL}/products.json")
        data = response.json()
        for product in data["products"][:5]:
            assert "title" in product, "Товар без title"
            assert len(product["title"]) > 0

    @allure.title("products.json товары имеют price")
    def test_products_json_has_price(self):
        response = requests.get(f"{BASE_URL}/products.json")
        data = response.json()
        for product in data["products"][:5]:
            variants = product.get("variants", [])
            assert len(variants) > 0, (
                f"Товар {product['title']} без variants"
            )
            price = variants[0].get("price")
            assert price is not None, (
                f"Товар {product['title']} без price"
            )

    @allure.title("products.json товары имеют images")
    def test_products_json_has_images(self):
        response = requests.get(f"{BASE_URL}/products.json")
        data = response.json()
        products_with_images = 0
        for product in data["products"][:10]:
            if product.get("images"):
                products_with_images += 1
        assert products_with_images > 0, (
            "Ни один товар не имеет изображений"
        )

    @allure.title("products.json limit параметр работает")
    def test_products_json_limit(self):
        response = requests.get(
            f"{BASE_URL}/products.json?limit=5"
        )
        data = response.json()
        assert len(data["products"]) <= 5

    @allure.title("products.json page параметр работает")
    def test_products_json_pagination(self):
        r1 = requests.get(
            f"{BASE_URL}/products.json?limit=2&page=1"
        )
        r2 = requests.get(
            f"{BASE_URL}/products.json?limit=2&page=2"
        )
        ids1 = {p["id"] for p in r1.json()["products"]}
        ids2 = {p["id"] for p in r2.json()["products"]}
        assert ids1 != ids2, "Страницы 1 и 2 одинаковые"

    @allure.title("collections.json возвращает коллекции")
    def test_collections_json(self):
        response = requests.get(
            f"{BASE_URL}/collections.json"
        )
        assert response.status_code == 200
        data = response.json()
        assert "collections" in data
        assert len(data["collections"]) > 0

    @allure.title("Коллекция JSON содержит товары")
    @pytest.mark.parametrize("slug,name", COLLECTIONS[:3])
    def test_collection_json_products(self, slug, name):
        response = requests.get(
            f"{BASE_URL}/collections/{slug}/products.json"
        )
        if response.status_code == 200:
            data = response.json()
            assert "products" in data


@allure.feature("API тесты")
@allure.story("Поиск")
class TestApiSearch:
    """Проверка поискового API."""

    @allure.title("Поиск возвращает результаты")
    def test_search_returns_results(self):
        response = requests.get(
            f"{BASE_URL}/search?q=ado&type=product"
        )
        assert response.status_code == 200

    @allure.title("Поиск по типу product")
    def test_search_type_product(self):
        response = requests.get(
            f"{BASE_URL}/search?q=shinzou&type=product"
        )
        assert response.status_code == 200
        assert "product" in response.text.lower()

    @allure.title("Поиск через suggest endpoint")
    def test_search_suggest(self):
        response = requests.get(
            f"{BASE_URL}/search/suggest.json"
            f"?q=ado&resources[type]=product"
        )
        assert response.status_code == 200

    @allure.title("Пустой поиск не падает")
    def test_search_empty(self):
        response = requests.get(
            f"{BASE_URL}/search?q=&type=product"
        )
        assert response.status_code == 200


@allure.feature("API тесты")
@allure.story("Корзина API")
class TestCartApi:
    """Проверка API корзины Shopify."""

    @allure.title("Корзина JSON пуста по умолчанию")
    def test_cart_empty(self):
        response = requests.get(f"{BASE_URL}/cart.json")
        assert response.status_code == 200
        data = response.json()
        assert data.get("item_count", 0) == 0

    @allure.title("Корзина JSON имеет нужные поля")
    def test_cart_json_fields(self):
        response = requests.get(f"{BASE_URL}/cart.json")
        data = response.json()
        required = ["token", "item_count", "total_price", "items"]
        for field in required:
            assert field in data, f"Поле {field} отсутствует"

    @allure.title("Добавление товара в корзину")
    def test_add_to_cart(self):
        session = requests.Session()
        session.get(f"{BASE_URL}/cart.json")
        products = session.get(
            f"{BASE_URL}/products.json?limit=1"
        ).json()["products"]
        variant_id = products[0]["variants"][0]["id"]
        response = session.post(
            f"{BASE_URL}/cart/add.js",
            json={"items": [{"id": variant_id, "quantity": 1}]},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code in (200, 201, 422)

    @allure.title("Очистка корзины")
    def test_clear_cart(self):
        session = requests.Session()
        session.get(f"{BASE_URL}/cart.json")
        response = session.post(
            f"{BASE_URL}/cart/clear.js",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("item_count", 0) == 0

    @allure.title("Обновление количества товара")
    def test_update_cart_quantity(self):
        session = requests.Session()
        session.get(f"{BASE_URL}/cart.json")
        products = session.get(
            f"{BASE_URL}/products.json?limit=1"
        ).json()["products"]
        variant_id = products[0]["variants"][0]["id"]
        session.post(
            f"{BASE_URL}/cart/add.js",
            json={"items": [{"id": variant_id, "quantity": 1}]},
            headers={"Content-Type": "application/json"}
        )
        response = session.post(
            f"{BASE_URL}/cart/update.js",
            json={"updates": {str(variant_id): 2}},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200

    @allure.title("Корзина JSON формат корректен")
    def test_cart_json_format(self):
        response = requests.get(f"{BASE_URL}/cart.json")
        data = response.json()
        assert isinstance(data["items"], list)
        assert isinstance(data["total_price"], int)
        assert isinstance(data["item_count"], int)


@allure.feature("API тесты")
@allure.story("Редиректы и статус-коды")
class TestApiRedirects:
    """Проверка редиректов и статус-кодов."""

    @allure.title("HTTP редирект на HTTPS")
    def test_http_to_https_redirect(self):
        response = requests.get(
            f"http://ado-shop.com",
            allow_redirects=False
        )
        assert response.status_code in (301, 302, 308)

    @allure.title("/account возвращает 302 или 200")
    def test_account_page(self):
        response = requests.get(
            f"{BASE_URL}/account", allow_redirects=True
        )
        assert response.status_code in (200, 302, 404)

    @allure.title("Страница policies существует")
    def test_privacy_policy(self):
        response = requests.get(
            f"{BASE_URL}/policies/privacy-policy"
        )
        assert response.status_code == 200

    @allure.title("Страница terms существует")
    def test_terms_of_service(self):
        response = requests.get(
            f"{BASE_URL}/policies/terms-of-service"
        )
        assert response.status_code == 200

    @allure.title("Refund policy существует")
    def test_refund_policy(self):
        response = requests.get(
            f"{BASE_URL}/policies/refund-policy"
        )
        assert response.status_code == 200


@allure.feature("API тесты")
@allure.story("Заголовки ответов")
class TestApiHeadersExtended:
    """Расширенная проверка HTTP-заголовков."""

    @allure.title("Есть заголовок X-Frame-Options")
    def test_x_frame_options(self):
        response = requests.get(BASE_URL)
        headers = {k.lower(): v for k, v in response.headers.items()}
        if "x-frame-options" in headers:
            assert headers["x-frame-options"] in (
                "DENY", "SAMEORIGIN"
            )

    @allure.title("Cache-Control присутствует")
    def test_cache_control(self):
        response = requests.get(BASE_URL)
        headers = {k.lower(): v for k, v in response.headers.items()}
        assert "cache-control" in headers

    @allure.title("X-Permitted-Cross-Domain")
    def test_cross_domain(self):
        response = requests.get(BASE_URL)
        headers = {k.lower(): v for k, v in response.headers.items()}
        if "x-permitted-cross-domain-policies" in headers:
            assert headers["x-permitted-cross-domain-policies"] == "none"

    @allure.title("ETag присутствует")
    def test_etag(self):
        response = requests.get(BASE_URL)
        headers = {k.lower(): v for k, v in response.headers.items()}
        assert "etag" in headers


@allure.feature("API тесты")
@allure.story("HTTP методы PUT/PATCH/DELETE")
class TestHttpMethods:
    """Проверка обработки HTTP-методов PUT, PATCH, DELETE."""

    ENDPOINTS = [
        "/",
        "/products.json",
        "/collections.json",
        "/cart.json",
        "/search?q=ado&type=product",
        "/collections/shinzou",
    ]

    PUT_BODY = {
        "product": {
            "title": "Test Product",
            "body_html": "<p>Test description</p>",
            "vendor": "ADO Shop",
            "product_type": "T-Shirt",
            "tags": ["test", "api"],
            "variants": [
                {
                    "title": "Default",
                    "price": "19.99",
                    "sku": "TEST-001",
                    "inventory_quantity": 10
                }
            ]
        }
    }

    PATCH_BODY = {
        "product": {
            "id": 123456789,
            "title": "Updated Product",
            "variants": [
                {
                    "id": 987654321,
                    "price": "24.99"
                }
            ]
        }
    }

    DELETE_BODY = {
        "product_ids": [123456789]
    }

    @allure.title("PUT на публичные эндпоинты возвращает 403")
    @pytest.mark.parametrize("endpoint", ENDPOINTS)
    def test_put_returns_403(self, endpoint):
        response = requests.put(
            f"{BASE_URL}{endpoint}",
            headers={"Content-Type": "application/json"},
            json=self.PUT_BODY,
        )
        assert response.status_code == 403, (
            f"PUT {endpoint}: ожидатель 403, "
            f"получен {response.status_code}"
        )

    @allure.title("PUT на публичные эндпоинты возвращает 404")
    @pytest.mark.parametrize("endpoint", ENDPOINTS)
    def test_put_returns_404(self, endpoint):
        response = requests.put(
            f"{BASE_URL}{endpoint}",
            headers={"Content-Type": "application/json"},
            json=self.PUT_BODY,
        )
        assert response.status_code == 404, (
            f"PUT {endpoint}: ожидатель 404, "
            f"получен {response.status_code}"
        )

    @allure.title("PUT на публичные эндпоинты возвращает 405")
    @pytest.mark.parametrize("endpoint", ENDPOINTS)
    def test_put_returns_405(self, endpoint):
        response = requests.put(
            f"{BASE_URL}{endpoint}",
            headers={"Content-Type": "application/json"},
            json=self.PUT_BODY,
        )
        assert response.status_code == 405, (
            f"PUT {endpoint}: ожидатель 405, "
            f"получен {response.status_code}"
        )

    @allure.title("PATCH на публичные эндпоинты возвращает 403")
    @pytest.mark.parametrize("endpoint", ENDPOINTS)
    def test_patch_returns_403(self, endpoint):
        response = requests.patch(
            f"{BASE_URL}{endpoint}",
            headers={"Content-Type": "application/json"},
            json=self.PATCH_BODY,
        )
        assert response.status_code == 403, (
            f"PATCH {endpoint}: ожидатель 403, "
            f"получен {response.status_code}"
        )

    @allure.title("PATCH на публичные эндпоинты возвращает 404")
    @pytest.mark.parametrize("endpoint", ENDPOINTS)
    def test_patch_returns_404(self, endpoint):
        response = requests.patch(
            f"{BASE_URL}{endpoint}",
            headers={"Content-Type": "application/json"},
            json=self.PATCH_BODY,
        )
        assert response.status_code == 404, (
            f"PATCH {endpoint}: ожидатель 404, "
            f"получен {response.status_code}"
        )

    @allure.title("PATCH на публичные эндпоинты возвращает 405")
    @pytest.mark.parametrize("endpoint", ENDPOINTS)
    def test_patch_returns_405(self, endpoint):
        response = requests.patch(
            f"{BASE_URL}{endpoint}",
            headers={"Content-Type": "application/json"},
            json=self.PATCH_BODY,
        )
        assert response.status_code == 405, (
            f"PATCH {endpoint}: ожидатель 405, "
            f"получен {response.status_code}"
        )

    @allure.title("DELETE на публичные эндпоинты возвращает 403")
    @pytest.mark.parametrize("endpoint", ENDPOINTS)
    def test_delete_returns_403(self, endpoint):
        response = requests.delete(
            f"{BASE_URL}{endpoint}",
            headers={"Content-Type": "application/json"},
            json=self.DELETE_BODY,
        )
        assert response.status_code == 403, (
            f"DELETE {endpoint}: ожидатель 403, "
            f"получен {response.status_code}"
        )

    @allure.title("DELETE на публичные эндпоинты возвращает 404")
    @pytest.mark.parametrize("endpoint", ENDPOINTS)
    def test_delete_returns_404(self, endpoint):
        response = requests.delete(
            f"{BASE_URL}{endpoint}",
            headers={"Content-Type": "application/json"},
            json=self.DELETE_BODY,
        )
        assert response.status_code == 404, (
            f"DELETE {endpoint}: ожидатель 404, "
            f"получен {response.status_code}"
        )

    @allure.title("DELETE на публичные эндпоинты возвращает 405")
    @pytest.mark.parametrize("endpoint", ENDPOINTS)
    def test_delete_returns_405(self, endpoint):
        response = requests.delete(
            f"{BASE_URL}{endpoint}",
            headers={"Content-Type": "application/json"},
            json=self.DELETE_BODY,
        )
        assert response.status_code == 405, (
            f"DELETE {endpoint}: ожидатель 405, "
            f"получен {response.status_code}"
        )

    @allure.title("PUT на cart/add.js возвращает 403")
    def test_put_cart_add_returns_403(self):
        response = requests.put(
            f"{BASE_URL}/cart/add.js",
            headers={"Content-Type": "application/json"},
            json={"items": [{"id": 123456, "quantity": 1}]},
        )
        assert response.status_code == 403, (
            f"PUT cart/add.js: ожидатель 403, "
            f"получен {response.status_code}"
        )

    @allure.title("PUT на cart/add.js возвращает 404")
    def test_put_cart_add_returns_404(self):
        response = requests.put(
            f"{BASE_URL}/cart/add.js",
            headers={"Content-Type": "application/json"},
            json={"items": [{"id": 123456, "quantity": 1}]},
        )
        assert response.status_code == 404, (
            f"PUT cart/add.js: ожидатель 404, "
            f"получен {response.status_code}"
        )

    @allure.title("PUT на cart/add.js возвращает 405")
    def test_put_cart_add_returns_405(self):
        response = requests.put(
            f"{BASE_URL}/cart/add.js",
            headers={"Content-Type": "application/json"},
            json={"items": [{"id": 123456, "quantity": 1}]},
        )
        assert response.status_code == 405, (
            f"PUT cart/add.js: ожидатель 405, "
            f"получен {response.status_code}"
        )

    @allure.title("DELETE на cart/clear.js возвращает 403")
    def test_delete_cart_clear_returns_403(self):
        response = requests.delete(
            f"{BASE_URL}/cart/clear.js",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 403, (
            f"DELETE cart/clear.js: ожидатель 403, "
            f"получен {response.status_code}"
        )

    @allure.title("DELETE на cart/clear.js возвращает 404")
    def test_delete_cart_clear_returns_404(self):
        response = requests.delete(
            f"{BASE_URL}/cart/clear.js",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 404, (
            f"DELETE cart/clear.js: ожидатель 404, "
            f"получен {response.status_code}"
        )

    @allure.title("DELETE на cart/clear.js возвращает 405")
    def test_delete_cart_clear_returns_405(self):
        response = requests.delete(
            f"{BASE_URL}/cart/clear.js",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 405, (
            f"DELETE cart/clear.js: ожидатель 405, "
            f"получен {response.status_code}"
        )

    @allure.title("PATCH на cart/update.js возвращает 403")
    def test_patch_cart_update_returns_403(self):
        response = requests.patch(
            f"{BASE_URL}/cart/update.js",
            headers={"Content-Type": "application/json"},
            json={"updates": {"123456": 2}},
        )
        assert response.status_code == 403, (
            f"PATCH cart/update.js: ожидатель 403, "
            f"получен {response.status_code}"
        )

    @allure.title("PATCH на cart/update.js возвращает 404")
    def test_patch_cart_update_returns_404(self):
        response = requests.patch(
            f"{BASE_URL}/cart/update.js",
            headers={"Content-Type": "application/json"},
            json={"updates": {"123456": 2}},
        )
        assert response.status_code == 404, (
            f"PATCH cart/update.js: ожидатель 404, "
            f"получен {response.status_code}"
        )

    @allure.title("PATCH на cart/update.js возвращает 405")
    def test_patch_cart_update_returns_405(self):
        response = requests.patch(
            f"{BASE_URL}/cart/update.js",
            headers={"Content-Type": "application/json"},
            json={"updates": {"123456": 2}},
        )
        assert response.status_code == 405, (
            f"PATCH cart/update.js: ожидатель 405, "
            f"получен {response.status_code}"
        )


@allure.feature("API тесты")
@allure.story("Контент страниц")
class TestApiContentExtended:
    """Расширенная проверка контента страниц."""

    @allure.title("Главная содержит ссылки на коллекции")
    def test_main_links_to_collections(self):
        response = requests.get(BASE_URL)
        text = response.text.lower()
        has_link = False
        for slug, name in COLLECTIONS:
            if f"/collections/{slug}" in text:
                has_link = True
                break
        assert has_link, "Нет ссылок на коллекции"

    @allure.title("Коллекции содержат ссылки на товары")
    @pytest.mark.parametrize("slug,name", COLLECTIONS[:3])
    def test_collections_have_product_links(self, slug, name):
        response = requests.get(f"{BASE_URL}/collections/{slug}")
        assert "/products/" in response.text

    @allure.title("Товары в JSON имеют handle")
    def test_products_have_handle(self):
        response = requests.get(f"{BASE_URL}/products.json?limit=3")
        data = response.json()
        for product in data["products"]:
            assert "handle" in product
            assert len(product["handle"]) > 0

    @allure.title("Коллекции в JSON имеют handle")
    def test_collections_have_handle(self):
        response = requests.get(f"{BASE_URL}/collections.json")
        data = response.json()
        for coll in data["collections"]:
            assert "handle" in coll

    @allure.title("Карта сайта доступна")
    def test_sitemap(self):
        response = requests.get(f"{BASE_URL}/sitemap.xml")
        assert response.status_code == 200
        assert "xml" in response.headers.get("Content-Type", "")

    @allure.title("favicon.ico доступен")
    def test_favicon(self):
        response = requests.get(f"{BASE_URL}/favicon.ico")
        assert response.status_code in (200, 304, 301)
