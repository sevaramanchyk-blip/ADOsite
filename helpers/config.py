"""Конфигурация проекта: URL-адреса и список коллекций магазина."""

import os

# Базовый URL сайта без trailing slash (для API-запросов)
BASE_URL = os.getenv("BASE_URL") or "https://ado-shop.com"

# URL главной страницы с trailing slash (для переходов в браузере)
MAIN_URL = os.getenv("MAIN_URL") or "https://ado-shop.com/"

# Список коллекций: (slug, читаемое имя)
# Используется в параметризованных тестах для проверки всех коллекций
COLLECTIONS = [
    ("shinzou", "Shinzou"),
    ("2nd-original-album-zanmu", "Zanmu"),
    ("hibana", "Hibana"),
    ("ados-best-adobum", "Ado's Best Adobum"),
    ("phantom-siita", "Phantom Siita"),
    ("all-merch", "All Merch"),
]
