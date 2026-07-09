"""Конфигурация нагрузочного тестирования: список страниц для проверки."""

from helpers.config import MAIN_URL

# Страницы, которые открываются параллельно при нагрузочном тесте
PAGES = [
    MAIN_URL,
    f"{MAIN_URL}collections/all-merch",
    f"{MAIN_URL}collections/shinzou",
    f"{MAIN_URL}collections/2nd-original-album-zanmu",
    f"{MAIN_URL}collections/hibana",
    f"{MAIN_URL}collections/ados-best-adobum",
    f"{MAIN_URL}collections/phantom-siita",
]
