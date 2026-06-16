import requests
import pytest
import allure


@allure.feature('Тесты api')
@allure.story('Проверка статус кода')
class TestApiAdoSite():
    @allure.title('Проверка статус кода')
    @pytest.mark.parametrize('status_code, name_site, url', [
        (200, 'https://ado-shop.com/',
         "https://ado-shop.com/"),
        (200, 'https://ado-shop.com/',
         "https://ado-shop.com/collections/all-merch"),
        (200, 'https://ado-shop.com/',
         "https://ado-shop.com/collections/shinzou"),
        (200, 'https://ado-shop.com/',
         "https://ado-shop.com/collections/"
         "2nd-original-album-zanmu"),
        (200, 'https://ado-shop.com/',
         "https://ado-shop.com/collections/hibana"),
        (200, 'https://ado-shop.com/',
         "https://ado-shop.com/collections/"
         "ados-best-adobum"),
        (200, 'https://ado-shop.com/',
         "https://ado-shop.com/collections/"
         "phantom-siita"),
    ])
    def test_api_ado_site(self, status_code, name_site, url):
        with allure.step('Вызов ручки'):
            response = requests.get(url=url)
        with allure.step(
            f'Проверка статус кода страницы {name_site}'
        ):
            assert response.status_code == status_code
