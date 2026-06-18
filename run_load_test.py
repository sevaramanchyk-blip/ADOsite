"""Модуль нагрузочного тестирования ado-shop.com.

Запускает несколько headless Chrome-браузеров, которые параллельно
открывают страницы сайта и замеряют время загрузки.
Результаты агрегируются в статистику (среднее, P95, RPS и т.д.).
"""

import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from helpers.load_config import PAGES


def _make_driver():
    """Создаёт headless Chrome-драйвер с настройками для нагрузочного теста."""
    opts = Options()
    opts.add_argument("--headless=new")       # Режим без окна (headless)
    opts.add_argument("--no-sandbox")         # Отключает песочницу (нужно в контейнерах)
    opts.add_argument("--disable-dev-shm-usage")  # Уменьшает потребление /dev/shm
    opts.add_argument("--disable-gpu")        # Отключаем GPU-ускорение (не нужно в headless)
    opts.add_argument("--window-size=1920,1080")   # Фиксируем размер окна для консистентности
    return webdriver.Chrome(options=opts)


def _worker(worker_id, urls, duration):
    """Рабочий поток: открывает страницы циклически в течение duration секунд.

    Args:
        worker_id: ID потока (для логирования).
        urls: список URL для циклического перебора.
        duration: длительность работы в секундах.

    Returns:
        Список словарей с результатами каждого запроса.
    """
    results = []
    driver = None
    try:
        driver = _make_driver()
        # Вычисляем момент окончания работы
        end_time = time.time() + duration
        i = 0
        # Цикл работает до истечения времени
        while time.time() < end_time:
            # Циклически перебираем URL (round-robin)
            url = urls[i % len(urls)]
            start = time.time()
            try:
                driver.get(url)
                load_time = time.time() - start
                title = driver.title
                results.append({
                    "url": url,
                    "time": load_time,
                    "status": "ok",
                    "title": title,
                })
            except Exception as e:
                # Ловим ошибки загрузки (таймауты, ошибки сети и т.д.)
                load_time = time.time() - start
                results.append({
                    "url": url,
                    "time": load_time,
                    "status": "error",
                    "error": str(e)[:80],  # Ограничиваем длину текста ошибки
                })
            i += 1
    finally:
        # Гарантируем закрытие браузера при выходе
        if driver:
            try:
                driver.quit()
            except Exception:
                pass
    return results


def run_load_test(users=10, ramp_up=5, duration_str="30s"):
    """Запускает нагрузочный тест и возвращает агрегированную статистику.

    Args:
        users: количество параллельных браузеров.
        ramp_up: время разгона (сек), пока не используется.
        duration_str: длительность теста (например, "30s").

    Returns:
        Словарь с HTML-текстом результатов или ошибкой.
    """
    # Парсим длительность из строки (убираем "s", если есть)
    try:
        duration = int(duration_str.replace("s", ""))
    except ValueError:
        duration = 30

    all_results = []
    start = time.time()

    # Запускаем пул потоков, каждый поток — один браузер
    with ThreadPoolExecutor(max_workers=users) as pool:
        futures = []
        for i in range(users):
            futures.append(pool.submit(_worker, i, PAGES, duration))
        # Собираем результаты по мере завершения потоков
        for f in as_completed(futures):
            all_results.extend(f.result())

    elapsed = round(time.time() - start, 1)

    # Разделяем результаты на успешные и ошибочные
    ok = [r for r in all_results if r["status"] == "ok"]
    fail = [r for r in all_results if r["status"] == "error"]
    times = [r["time"] for r in ok]

    total = len(all_results)
    success = len(ok)

    if not times:
        return {
            "error": f"Нет успешных запросов. Ошибок: {len(fail)}"
        }

    # Рассчитываем статистику времени отклика
    avg_time = round(statistics.mean(times), 2)          # Среднее время
    p95 = round(sorted(times)[int(len(times) * 0.95)], 2) # 95-й перцентиль
    min_time = round(min(times), 2)                        # Минимальное
    max_time = round(max(times), 2)                        # Максимальное
    rps = round(total / elapsed, 1) if elapsed > 0 else 0  # Запросов в секунду

    # Формируем HTML-текст с результатами для Telegram
    text = (
        f"<b>⚡ Нагрузочный тест — результаты</b>\n"
        f"<code>"
        f"Пользователей: {users}\n"
        f"Длительность: {duration}с (факт {elapsed}с)\n"
        f"Всего запросов: {total}\n"
        f"Успешных: {success} | Ошибок: {len(fail)}\n"
        f"Успешность: {round(success/total*100)}%\n"
        f"RPS: {rps}\n\n"
        f"Время отклика (сек):\n"
        f"  Среднее: {avg_time}\n"
        f"  Мин:     {min_time}\n"
        f"  Макс:   {max_time}\n"
        f"  P95:     {p95}"
        f"</code>"
    )

    # Добавляем уникальные ошибки (макс. 5), если они были
    if fail:
        errors = set(r["error"] for r in fail)
        text += "\n\n<b>Ошибки:</b>\n"
        for err in list(errors)[:5]:
            text += f"  • <code>{err}</code>\n"

    return {"text": text}
