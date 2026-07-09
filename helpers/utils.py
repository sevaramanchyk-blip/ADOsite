"""Утилиты: извлечение текста со страницы и поиск опечаток."""

import re
from selenium.webdriver.common.by import By

# Словарь распространённых опечаток: {неправильно: правильно}
COMMON_TYPOS = {
    "teh": "the",
    "recieve": "receive",
    "occured": "occurred",
    "seperate": "separate",
    "definately": "definitely",
    "accomodate": "accommodate",
    "occurence": "occurrence",
    "neccessary": "necessary",
    "priviledge": "privilege",
    "accomodation": "accommodation",
    "adn": "and",
    "taht": "that",
    "wiht": "with",
    "nto": "not",
    "fo": "of",
    "ot": "to",
    "nad": "and",
    "th e": "the",
    "t he": "the",
}


def get_visible_text(driver):
    """Извлекает видимый текст со всех элементов страницы."""
    elements = driver.find_elements(
        By.CSS_SELECTOR,
        "h1, h2, h3, h4, h5, h6, p, span, a, "
        "button, label, li, td, th, div"
    )
    texts = []
    for el in elements:
        try:
            if el.is_displayed() and el.text.strip():
                texts.append(el.text.strip())
        except Exception:
            pass
    return texts


def find_typos(texts):
    """Ищет опечатки в списке текстов по словарю COMMON_TYPOS."""
    found = []
    for text in texts:
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        for word in words:
            for typo, fix in COMMON_TYPOS.items():
                if word == typo:
                    found.append((word, fix, text[:60]))
    return found
