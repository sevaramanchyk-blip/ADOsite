"""Locust-файл для нагрузочного тестирования: поведение виртуального пользователя."""

from locust import HttpUser, task, between


class AdoShopUser(HttpUser):
    """Виртуальный пользователь, имитирующий реальные действия на сайте."""

    wait_time = between(1, 3)  # Пауза 1-3 сек между запросами

    @task(5)
    def index_page(self):
        self.client.get("/")

    @task(3)
    def collection_merch(self):
        self.client.get("/collections/all-merch")

    @task(2)
    def collection_shinzou(self):
        self.client.get("/collections/shinzou")

    @task(2)
    def collection_hibana(self):
        self.client.get("/collections/hibana")

    @task(2)
    def collection_zanmu(self):
        self.client.get("/collections/2nd-original-album-zanmu")

    @task(1)
    def collection_adobum(self):
        self.client.get("/collections/ados-best-adobum")

    @task(1)
    def collection_phantom(self):
        self.client.get("/collections/phantom-siita")
