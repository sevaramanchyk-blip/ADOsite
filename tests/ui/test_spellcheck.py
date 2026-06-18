"""Тесты проверки орфографии на сайте ado-shop.com."""
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from helpers.config import MAIN_URL
from helpers.utils import get_visible_text, find_typos


@allure.feature("Орфография")
@allure.story("Проверка опечаток")
class TestSpellCheck:
    """Проверка отсутствия опечаток на страницах сайта."""
    @allure.title("Нет типичных опечаток на главной")
    def test_main_page_typos(self, driver):
        driver.get(MAIN_URL)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        texts = get_visible_text(driver)
        typos = find_typos(texts)
        with allure.step(f"Проверено {len(texts)} элементов"):
            pass
        if typos:
            msg = "Найдены опечатки:\n"
            for word, fix, context in typos:
                msg += f"  '{word}' -> '{fix}' (в: {context})\n"
            assert False, msg

    @allure.title("Нет опечаток в хедере")
    def test_header_typos(self, driver):
        driver.get(MAIN_URL)
        wait = WebDriverWait(driver, 15)
        header = wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "header"))
        )
        texts = [header.text]
        typos = find_typos(texts)
        with allure.step(f"Проверен хедер"):
            assert len(typos) == 0, (
                f"Опечатки в хедере: {typos}"
            )

    @allure.title("Нет опечаток в футере")
    def test_footer_typos(self, driver):
        driver.get(MAIN_URL)
        wait = WebDriverWait(driver, 15)
        footer = wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "footer"))
        )
        texts = [footer.text]
        typos = find_typos(texts)
        with allure.step(f"Проверен футер"):
            assert len(typos) == 0, (
                f"Опечатки в футере: {typos}"
            )

    @allure.title("Нет опечаток в описании товаров")
    def test_product_text_typos(self, driver):
        driver.get(f"{MAIN_URL}collections/shinzou")
        wait = WebDriverWait(driver, 15)
        cards = wait.until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR,
                 ".card-wrapper, .product-card, "
                 "[class*='product']")
            )
        )
        texts = []
        for card in cards[:5]:
            try:
                if card.text.strip():
                    texts.append(card.text.strip())
            except Exception:
                pass
        typos = find_typos(texts)
        with allure.step(f"Проверено {len(cards)} карточек"):
            assert len(typos) == 0, (
                f"Опечатки в товарах: {typos}"
            )
