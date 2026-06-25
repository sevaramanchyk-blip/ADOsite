import os

MAIN_URL = os.getenv("MAIN_URL") or "https://ado-shop.com/"
BASE_URL = os.getenv("BASE_URL") or "https://ado-shop.com"

COLLECTIONS = [
    ("shinzou", "Shinzou"),
    ("2nd-original-album-zanmu", "Zanmu"),
    ("hibana", "Hibana"),
    ("ados-best-adobum", "Ado's Best Adobum"),
    ("phantom-siita", "Phantom Siita"),
    ("all-merch", "All Merch"),
]
