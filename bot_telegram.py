"""
Telegram-бот для запуска тестов сайта ado-shop.com.

Предоставляет интерактивное меню для запуска различных типов тестов:
API, UI, нагрузочных, проверки орфографии, отображения элементов
и бизнес-сценариев. Результаты оформляются в виде красивых
сообщений с эмодзи и статистикой.
"""

import asyncio
import os
import re
import sys
import signal
import warnings
from pathlib import Path
from html import escape as html_escape

warnings.filterwarnings("ignore", category=ResourceWarning)
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes
)

# Файл для хранения PID текущего процесса (блокировка повторного запуска)
PID_FILE = Path(__file__).parent / ".bot.pid"


def acquire_lock():
    """Проверяет, не запущен ли уже бот. Если запущен — завершает работу."""
    if PID_FILE.exists():
        old_pid = int(PID_FILE.read_text().strip())
        # Проверяем, жив ли процесс с сохранённым PID
        try:
            os.kill(old_pid, 0)
            print(
                f"Бот уже запущен (PID {old_pid}). "
                "Завершите предыдущий процесс."
            )
            sys.exit(1)
        except (OSError, SystemError):
            # Процесс не найден — удаляем устаревший PID-файл
            PID_FILE.unlink()
    # Сохраняем PID текущего процесса
    PID_FILE.write_text(str(os.getpid()))


def release_lock(signum=None, frame=None):
    """Удаляет PID-файл при завершении работы бота."""
    if PID_FILE.exists():
        PID_FILE.unlink()
    sys.exit(0)


# Данные о песнях Ado: (название, год, описание, ссылка YouTube)
ADO_SONGS = [
    (
        "Usseewa", "2020",
        "Дебютный сингл. Протестная песня "
        "против societal pressures. "
        "Вирусный хит с 300M+ просмотров.",
        "https://www.youtube.com/watch?v=Qp3b-RXtz4w"
    ),
    (
        "Readymade", "2020",
        "Партёрная работа с продюсером TeddyLoid. "
        "Тёмный электронный звук.",
        "https://www.youtube.com/watch?v=jg09lNupc1s"
    ),
    (
        "Gira Gira", "2021",
        "Сингл из альбома Kyogen. "
        "Необычный визуал и мощный вокал.",
        "https://www.youtube.com/watch?v=sOiMD45QGLs"
    ),
    (
        "Odo", "2021",
        "Танцевальный трек для "
        "Project SEKAI. Энергичный бит.",
        "https://www.youtube.com/watch?v=YnSW8ian29w"
    ),
    (
        "Aishite Aishite Aishite", "2021",
        "Эмоциональный трек о тёмной стороне "
        "популярности. Один из самых "
        "популярных клипов.",
        "https://www.youtube.com/watch?v=fZPY-CCesko"
    ),
    (
        "Kura Kura", "2021",
        "Сингл для аниме Spy x Family. "
        "Яркий и динамичный.",
        "https://www.youtube.com/watch?v=gz--GkzpAf8"
    ),
    (
        "Show", "2022",
        "Саундтрек к One Piece Film Red. "
        "Мощная рок-баллада.",
        "https://www.youtube.com/watch?v=pgXpM4l_MwI"
    ),
    (
        "Yoru no Pierrot", "2022",
        "Коллаборация с Giga. "
        "Электронный трек с цирковым вайбом.",
        "https://www.youtube.com/watch?v=cSgZxz3le7s"
    ),
    (
        "New Genesis", "2022",
        "Главный сингл One Piece Film Red. "
        "Гимн свободы и нового начала.",
        "https://www.youtube.com/watch?v=1FliVTcX8bQ"
    ),
    (
        "Freedom", "2022",
        "Партёрная работа с Vaundy. "
        "Рок-трек о свободе выбора.",
        "https://www.youtube.com/watch?v=hgyGhu49sGc"
    ),
    (
        "Shoka", "2022",
        "Коллаборация с Milet для "
        "One Piece Film Red. Нежный вокал.",
        "https://www.youtube.com/watch?v=GORsp0gc2Nc"
    ),
    (
        "Rockstar", "2023",
        "Энергичный трек с альбома Zanmu. "
        "Про жизнь рок-звезды.",
        "https://www.youtube.com/watch?v=hRJpiCZlLX8"
    ),
    (
        "Hibana", "2024",
        "Сингл из альбома Hibana. "
        "Мощный рок с японскими мотивами.",
        "https://www.youtube.com/watch?v=EFsSYiNl2AQ"
    ),
    (
        "Tokyo Cannibalism", "2024",
        "Провокационный трек. "
        "Тёмная электроника и социальная сатира.",
        "https://www.youtube.com/watch?v=zpu9V9lUVhw"
    ),
]

# Разделитель для визуального оформления сообщений
SEP = "━━━━━━━━━━━━━━━━━━━━"

# Главное меню бота — инлайн-кнопки для выбора действий
MAIN_MENU = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(
            "🚀 API тесты", callback_data="run_api"
        ),
        InlineKeyboardButton(
            "🌐 UI тесты", callback_data="run_ui"
        ),
    ],
    [
        InlineKeyboardButton(
            "⚡ Нагрузочный тест", callback_data="run_load"
        ),
        InlineKeyboardButton(
            "📝 Орфография", callback_data="run_spell"
        ),
    ],
    [
        InlineKeyboardButton(
            "👁 Элементы", callback_data="run_elements"
        ),
        InlineKeyboardButton(
            "💼 Сценарии", callback_data="run_business"
        ),
    ],
    [
        InlineKeyboardButton(
            "🔄 Все тесты", callback_data="run_all"
        ),
        InlineKeyboardButton(
            "📊 Статистика", callback_data="stats"
        ),
    ],
    [
        InlineKeyboardButton(
            "📋 Отчёт", callback_data="last_report"
        ),
        InlineKeyboardButton(
            "⚙️ Настройки", callback_data="settings"
        ),
    ],
    [
        InlineKeyboardButton(
            "🎤 Про Ado", callback_data="about_ado"
        ),
        InlineKeyboardButton(
            "🎵 Песни Ado", callback_data="ado_songs"
        ),
    ],
    [
        InlineKeyboardButton(
            "👤 Обо мне", callback_data="about_me"
        ),
        InlineKeyboardButton(
            "🛒 Магазин ADO", callback_data="about_site"
        ),
    ],
    [
        InlineKeyboardButton(
            "🔗 Ссылки", callback_data="run_links"
        ),
    ],
])


async def safe_answer(query):
    """Безопасно отвечает на callback query (игнорирует expired)."""
    try:
        await query.answer()
    except Exception:
        pass


async def execute_command(cmd: str, timeout: int = 300) -> str:
    """Выполняет shell-команду с таймаутом и возвращает stdout/stderr."""
    proc = None
    try:
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(), timeout
        )
        output = (
            f"STDOUT:\n{stdout.decode().strip()}"
            if stdout else ''
        )
        output += (
            f"\nSTDERR:\n{stderr.decode().strip()}"
            if stderr else ''
        )
        return output.strip()
    except asyncio.TimeoutError:
        return f"Таймаут {timeout} сек"
    except Exception as e:
        return f'Ошибка {str(e)}'
    finally:
        if proc and proc.returncode is None:
            try:
                proc.kill()
                await proc.wait()
            except Exception:
                pass


def clear_results():
    """Очищает папку results перед запуском новых тестов."""
    results_dir = Path("./results")
    results_dir.mkdir(exist_ok=True)
    for file in results_dir.glob("*"):
        file.unlink()


async def cleanup_messages(
    context, chat_id, user_data, except_id=None
):
    """Удаляет предыдущие сообщения бота, кроме текущего (except_id)."""
    old_ids = user_data.get("bot_msg_ids", [])
    user_data["bot_msg_ids"] = []
    for msg_id in old_ids:
        if msg_id == except_id:
            continue
        try:
            await context.bot.delete_message(chat_id, msg_id)
        except Exception:
            pass


async def track_message(context, chat_id, msg, user_data):
    """Сохраняет ID сообщения для последующей очистки."""
    user_data.setdefault("bot_msg_ids", []).append(
        msg.message_id
    )


def _truncate(text, max_len=4000):
    """Обрезает текст по строкам, не ломая HTML-теги.

    Если сообщение длиннее max_len — обрезает на последнем переносе
    строки перед лимитом и добавляет пометку (обрезано).
    Лимит 4000 — максимальная длина сообщения в Telegram (4096 минус запас).
    """
    if len(text) <= max_len:
        return text
    cut = text[:max_len]
    last_nl = cut.rfind('\n')
    if last_nl > max_len - 200:
        cut = cut[:last_nl]
    return cut + "\n\n... <i>(обрезано)</i>"


def _parse_pytest_output(result: str):
    """Парсит вывод pytest, извлекая PASSED/FAILED тесты.

    Обрабатывает два формата вывода:
    1) tests/file.py::TestClass::test_name PASSED [ 10%]
    2) FAILED tests/file.py::TestClass::test_name — traceback
    """
    lines = result.split('\n')
    passed = []
    failed = []
    errors = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Формат 2: "FAILED tests/..." на отдельной строке (short test summary)
        if stripped.startswith('FAILED'):
            match = re.search(r'FAILED\s+(.+?)(?:\s+-|$)', stripped)
            if match:
                name = match.group(1).strip()
                if '::' in name:
                    name = name.split('::')[-1]
                failed.append(name)

        # Формат 1: "tests/file.py::test_name PASSED [ 10%]"
        elif 'PASSED' in line or 'FAILED' in line:
            match = re.search(r'(.+?)\s+(PASSED|FAILED)', line)
            if match:
                name = match.group(1).strip()
                status = match.group(2)
                if '::' in name:
                    name = name.split('::')[-1]
                if status == 'PASSED':
                    passed.append(name)
                else:
                    failed.append(name)

        elif 'ERROR' in line and 'error' in line.lower():
            errors.append(line.strip())

        i += 1

    return passed, failed, errors


def format_api_results(result: str) -> str:
    """Форматирует результаты API тестов в HTML-таблицу."""
    passed, failed, errors = _parse_pytest_output(result)

    total = len(passed) + len(failed)
    success_rate = len(passed) / total * 100 if total > 0 else 0

    table = f"🚀 <b>API тесты</b> — {len(passed)}/{total}\n"
    table += f"<code>✅ {len(passed)} | ❌ {len(failed)} | {success_rate:.0f}%</code>\n"

    if passed:
        table += "<b>Пройденные:</b>\n"
        for name in passed:
            table += f"  ✅ {html_escape(name)}\n"

    if failed:
        table += "<b>Проваленные:</b>\n"
        for name in failed:
            table += f"  ❌ {html_escape(name)}\n"

    if errors:
        table += "<b>Ошибки сборки:</b>\n"
        for err in errors[:3]:
            table += f"  ⚠️ {html_escape(err[:80])}\n"

    return _truncate(table)


def format_ui_results(result: str) -> str:
    """Форматирует результаты UI тестов в HTML-таблицу."""
    passed, failed, errors = _parse_pytest_output(result)

    total = len(passed) + len(failed)
    success_rate = len(passed) / total * 100 if total > 0 else 0

    table = f"🌐 <b>UI тесты</b> — {len(passed)}/{total}\n"
    table += f"<code>✅ Пройдено: {len(passed)} | ❌ Провалено: {len(failed)} | 📊 {success_rate:.0f}%</code>\n"

    if passed:
        table += "<b>Пройденные:</b>\n"
        for name in passed:
            table += f"  ✅ {html_escape(name)}\n"

    if failed:
        table += "<b>Проваленные:</b>\n"
        for name in failed:
            table += f"  ❌ {html_escape(name)}\n"

    return _truncate(table)


def format_load_results(result: str) -> str:
    """Форматирует результаты нагрузочного теста в HTML-таблицу."""
    passed, failed, errors = _parse_pytest_output(result)

    total = len(passed) + len(failed)
    success_rate = len(passed) / total * 100 if total > 0 else 0

    table = f"⚡ <b>Нагрузочный тест</b> — {len(passed)}/{total}\n"
    table += f"<code>✅ Пройдено: {len(passed)} | ❌ Провалено: {len(failed)} | 📊 {success_rate:.0f}%</code>\n"

    if passed:
        table += "<b>Пройденные:</b>\n"
        for name in passed:
            table += f"  ✅ {html_escape(name)}\n"

    if failed:
        table += "<b>Проваленные:</b>\n"
        for name in failed:
            table += f"  ❌ {html_escape(name)}\n"

    return _truncate(table)


def format_results_generic(result: str, label: str, icon: str) -> str:
    """Универсальный форматировщик: принимает label и icon для шапки."""
    passed, failed, errors = _parse_pytest_output(result)

    total = len(passed) + len(failed)
    success_rate = len(passed) / total * 100 if total > 0 else 0

    table = f"{icon} <b>{label}</b> — {len(passed)}/{total}\n"
    table += f"<code>✅ Пройдено: {len(passed)} | ❌ Провалено: {len(failed)} | 📊 {success_rate:.0f}%</code>\n"

    if passed:
        table += "<b>Пройденные:</b>\n"
        for name in passed:
            table += f"  ✅ {html_escape(name)}\n"

    if failed:
        table += "<b>Проваленные:</b>\n"
        for name in failed:
            table += f"  ❌ {html_escape(name)}\n"

    return _truncate(table)


async def start(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Обработчик команды /start — показывает главное меню."""
    chat_id = update.effective_chat.id
    await cleanup_messages(context, chat_id, context.user_data)
    msg = await update.message.reply_text(
        f"╔══════════════════════╗\n"
        f"║   🎵 ADO SHOP BOT   ║\n"
        f"╚══════════════════════╝\n\n"
        f"Привет! Я бот для тестирования\n"
        f"ADO Official Music Shop 🎶\n\n"
        f"Выбери действие из меню ниже 👇",
        reply_markup=MAIN_MENU
    )
    await track_message(context, chat_id, msg, context.user_data)


async def run_api_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Обработчик команды /run_api_test — запуск API тестов из чата."""
    chat_id = update.effective_chat.id
    await cleanup_messages(context, chat_id, context.user_data)
    msg = await update.message.reply_text('🚀 Запуск API тестов...')
    await track_message(context, chat_id, msg, context.user_data)
    clear_results()
    result = await execute_command(
        'pytest -v tests/api --tb=no'
    )
    text = format_api_results(result)
    msg = await update.message.reply_text(
        text, parse_mode='HTML',
        reply_markup=MAIN_MENU
    )
    await track_message(context, chat_id, msg, context.user_data)


async def run_ui_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Обработчик команды /run_ui_test — запуск UI тестов из чата."""
    chat_id = update.effective_chat.id
    await cleanup_messages(context, chat_id, context.user_data)
    msg = await update.message.reply_text('🌐 Запуск UI тестов...')
    await track_message(context, chat_id, msg, context.user_data)
    clear_results()
    result = await execute_command(
        'pytest -v tests/ui --tb=no', timeout=600
    )
    text = format_ui_results(result)
    msg = await update.message.reply_text(
        text, parse_mode='HTML',
        reply_markup=MAIN_MENU
    )
    await track_message(context, chat_id, msg, context.user_data)


async def callback_run_api(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Обработчик кнопки 'API тесты' — запуск API тестов."""
    query = update.callback_query
    chat_id = query.message.chat_id
    await safe_answer(query)
    await cleanup_messages(
        context, chat_id, context.user_data,
        except_id=query.message.message_id
    )
    msg = await query.message.reply_text(
        "🚀 Запуск API тестов..."
    )
    await track_message(context, chat_id, msg, context.user_data)
    clear_results()
    result = await execute_command(
        'pytest -v tests/api --tb=no'
    )
    text = format_api_results(result)
    msg = await query.message.reply_text(
        text, parse_mode='HTML'
    )
    await track_message(context, chat_id, msg, context.user_data)


async def callback_run_ui(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Обработчик кнопки 'UI тесты' — запуск UI тестов."""
    query = update.callback_query
    chat_id = query.message.chat_id
    await safe_answer(query)
    await cleanup_messages(
        context, chat_id, context.user_data,
        except_id=query.message.message_id
    )
    msg = await query.message.reply_text(
        "🌐 Запуск UI тестов..."
    )
    await track_message(context, chat_id, msg, context.user_data)
    clear_results()
    result = await execute_command(
        'pytest -v tests/ui --tb=no', timeout=600
    )
    text = format_ui_results(result)
    msg = await query.message.reply_text(
        text, parse_mode='HTML'
    )
    await track_message(context, chat_id, msg, context.user_data)


async def callback_run_spell(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Обработчик кнопки 'Орфография' — проверка орфографии на сайте."""
    query = update.callback_query
    chat_id = query.message.chat_id
    await safe_answer(query)
    await cleanup_messages(
        context, chat_id, context.user_data,
        except_id=query.message.message_id
    )
    msg = await query.message.reply_text(
        "📝 Запуск проверки орфографии..."
    )
    await track_message(context, chat_id, msg, context.user_data)
    clear_results()
    result = await execute_command(
        'pytest -v tests/ui/test_spellcheck.py --tb=no'
    )
    text = format_results_generic(
        result, "Проверка орфографии", "📝"
    )
    msg = await query.message.reply_text(
        text, parse_mode='HTML'
    )
    await track_message(context, chat_id, msg, context.user_data)


async def callback_run_elements(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Обработчик кнопки 'Элементы' — проверка отображения элементов."""
    query = update.callback_query
    chat_id = query.message.chat_id
    await safe_answer(query)
    await cleanup_messages(
        context, chat_id, context.user_data,
        except_id=query.message.message_id
    )
    msg = await query.message.reply_text(
        "👁 Запуск проверки отображения элементов..."
    )
    await track_message(context, chat_id, msg, context.user_data)
    clear_results()
    result = await execute_command(
        'pytest -v tests/ui/test_elements.py --tb=no'
    )
    text = format_results_generic(
        result, "Отображение элементов", "👁"
    )
    msg = await query.message.reply_text(
        text, parse_mode='HTML'
    )
    await track_message(context, chat_id, msg, context.user_data)


async def callback_run_business(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Обработчик кнопки 'Сценарии' — запуск бизнес-сценариев."""
    query = update.callback_query
    chat_id = query.message.chat_id
    await safe_answer(query)
    await cleanup_messages(
        context, chat_id, context.user_data,
        except_id=query.message.message_id
    )
    msg = await query.message.reply_text(
        "💼 Запуск бизнес-сценариев..."
    )
    await track_message(context, chat_id, msg, context.user_data)
    clear_results()
    result = await execute_command(
        'pytest -v tests/ui/test_business.py --tb=no'
    )
    text = format_results_generic(
        result, "Бизнес-сценарии", "💼"
    )
    msg = await query.message.reply_text(
        text, parse_mode='HTML'
    )
    await track_message(context, chat_id, msg, context.user_data)


async def callback_about_ado(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Обработчик кнопки 'Про Ado' — показывает информацию об исполнителе."""
    query = update.callback_query
    chat_id = query.message.chat_id
    await safe_answer(query)
    await cleanup_messages(
        context, chat_id, context.user_data,
        except_id=query.message.message_id
    )
    await query.edit_message_text(
        f"🎤 <b>Ado (アド)</b>\n"
        f"{SEP}\n\n"
        f"Японская певица и автор песен,\n"
        f"одна из самых популярных\n"
        f"исполнительниц Японии.\n\n"
        f"━━━━ <b>Инфо</b> ━━━━\n"
        f"📅 Дата рождения: 24 октября 2002\n"
        f"🌏 Страна: Япония\n"
        f"🎶 Жанр: J-Pop, рок, электроника\n"
        f"💿 Дебют: 2020 (Usseewa)\n\n"
        f"━━━━ <b>Факты</b> ━━━━\n"
        f"🎬 Исполняла песню к аниме\n"
        f"   «One Piece Film Red» (2022)\n"
        f"🎭 Её голос обрабатывают фильтры —\n"
        f"   она не показывает лицо\n"
        f"🏆 Дебютный альбом «Kyogen» (2022)\n"
        f"   стал одним из самых продаваемых\n"
        f"🤝 Совместные работы с Vaundy,\n"
        f"   Giga, TeddyLoid и другими",
        parse_mode='HTML',
        reply_markup=MAIN_MENU
    )


async def callback_ado_songs(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Обработчик кнопки 'Песни Ado' — список песен с ссылками на YouTube."""
    query = update.callback_query
    chat_id = query.message.chat_id
    await safe_answer(query)
    await cleanup_messages(
        context, chat_id, context.user_data,
        except_id=query.message.message_id
    )
    # Удаляем сообщение с кнопками, отправляем список песен отдельно
    try:
        await context.bot.delete_message(
            chat_id, query.message.message_id
        )
    except Exception:
        pass
    # Формируем список песен с ссылками на YouTube
    links = f"🎵 <b>Песни Ado</b>\n{SEP}\n\n"
    for name, year, desc, url in ADO_SONGS:
        links += (
            f"🎵 <b>{name}</b> ({year})\n"
            f"<i>{desc}</i>\n"
            f"<a href=\"{url}\">▶️ Смотреть на YouTube</a>\n\n"
        )
    msg = await context.bot.send_message(
        chat_id, links, parse_mode="HTML"
    )
    await track_message(context, chat_id, msg, context.user_data)
    msg = await context.bot.send_message(
        chat_id, f"Выбери действие 👇",
        reply_markup=MAIN_MENU
    )
    await track_message(context, chat_id, msg, context.user_data)


async def callback_back_to_main(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Обработчик кнопки 'Назад' — возврат в главное меню."""
    query = update.callback_query
    await safe_answer(query)
    await query.edit_message_text(
        "Выбери действие 👇",
        reply_markup=MAIN_MENU
    )


async def callback_run_links(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Обработчик кнопки 'Ссылки' — проверка всех внутренних ссылок."""
    query = update.callback_query
    chat_id = query.message.chat_id
    await safe_answer(query)
    await cleanup_messages(
        context, chat_id, context.user_data,
        except_id=query.message.message_id
    )
    msg = await query.message.reply_text(
        "🔗 Проверка всех ссылок сайта..."
    )
    await track_message(context, chat_id, msg, context.user_data)
    clear_results()
    result = await execute_command(
        'pytest -v tests/ui/test_links.py --tb=no'
    )
    text = format_results_generic(
        result, "Проверка ссылок", "🔗"
    )
    msg = await query.message.reply_text(
        text, parse_mode='HTML'
    )
    await track_message(context, chat_id, msg, context.user_data)


async def callback_about_me(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Обработчик кнопки 'Обо мне' — визитка QA-инженера."""
    query = update.callback_query
    chat_id = query.message.chat_id
    await safe_answer(query)
    await cleanup_messages(
        context, chat_id, context.user_data,
        except_id=query.message.message_id
    )
    await query.edit_message_text(
        f"👤 <b>Всеволод Романчик</b>\n"
        f"💼 QA Automation Engineer\n{SEP}\n\n"
        f"━━━━ <b>Контакты</b> ━━━━\n"
        f"📧 seva.ramanchyk@gmail.com\n"
        f"📱 +375 (44) 758-27-67\n"
        f"📍 Минск, Беларусь\n\n"
        f"━━━━ <b>Навыки</b> ━━━━\n"
        f"🔹 Python / pytest\n"
        f"🔹 UI-автоматизация (Selenium)\n"
        f"🔹 API-тестирование (REST)\n"
        f"🔹 Allure / BDD (Cucumber)\n"
        f"🔹 CI/CD (GitHub Actions)\n"
        f"🔹 Docker\n\n"
        f"━━━━ <b>Инструменты</b> ━━━━\n"
        f"PyCharm, VS Code, Postman,\n"
        f"Swagger, Jira, TestRail, Playwright\n\n"
        f"━━━━ <b>Проект</b> ━━━━\n"
        f"ADO Official Music Shop —\n"
        f"автоматизация тестирования 🛒\n\n"
        f"🌐 <a href=\"https://ado-shop.com\">Сайт проекта</a>",
        parse_mode='HTML',
        reply_markup=MAIN_MENU
    )


async def callback_about_site(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Обработчик кнопки 'Магазин ADO' — информация о сайте ado-shop.com."""
    query = update.callback_query
    chat_id = query.message.chat_id
    await safe_answer(query)
    await cleanup_messages(
        context, chat_id, context.user_data,
        except_id=query.message.message_id
    )
    await query.edit_message_text(
        f"🛒 <b>ADO Official Music Shop</b>\n{SEP}\n"
        f"🌐 https://ado-shop.com/\n\n"
        f"Официальный магазин музыки и мерча\n"
        f"японской исполнительницы Ado 🎤\n\n"
        f"━━━━ <b>Каталог</b> ━━━━\n"
        f"💿 Коллекции: Shinzou, Hibana, Zanmu\n"
        f"👕 Мерч: альбомы, футболки, аксессуары\n\n"
        f"━━━━ <b>Платформа</b> ━━━━\n"
        f"💻 Shopify",
        parse_mode='HTML',
        reply_markup=MAIN_MENU
    )


async def callback_run_all(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Обработчик кнопки 'Все тесты' — запуск всех тестов по очереди."""
    query = update.callback_query
    chat_id = query.message.chat_id
    await safe_answer(query)
    await cleanup_messages(
        context, chat_id, context.user_data,
        except_id=query.message.message_id
    )
    msg = await query.message.reply_text(
        "🔄 Запуск всех тестов..."
    )
    await track_message(context, chat_id, msg, context.user_data)
    clear_results()
    result = await execute_command(
        'pytest -v tests/api tests/ui --tb=no', timeout=600
    )
    text = format_results_generic(
        result, "Все тесты", "🔄"
    )
    msg = await query.message.reply_text(
        text, parse_mode='HTML'
    )
    await track_message(context, chat_id, msg, context.user_data)


async def callback_stats(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Обработчик кнопки 'Статистика' — показать статистику тестов."""
    query = update.callback_query
    chat_id = query.message.chat_id
    await safe_answer(query)
    await cleanup_messages(
        context, chat_id, context.user_data,
        except_id=query.message.message_id
    )
    results_dir = Path("./results")
    total_files = len(list(results_dir.glob("*"))) if results_dir.exists() else 0
    tests_dir = Path("./tests")
    api_tests = len(list(tests_dir.glob("api/test_*.py")))
    ui_tests = len(list(tests_dir.glob("ui/test_*.py")))
    bot_tests = len(list(tests_dir.glob("test_bot.py")))
    total_test_files = api_tests + ui_tests + bot_tests
    await query.edit_message_text(
        f"📊 <b>Статистика тестов</b>\n{SEP}\n\n"
        f"📁 Файлов результатов: {total_files}\n"
        f"📄 Файлов тестов: {total_test_files}\n"
        f"  🚀 API: {api_tests}\n"
        f"  🌐 UI: {ui_tests}\n"
        f"  🤖 Бот: {bot_tests}\n\n"
        f"━━━━ <b>Команды</b> ━━━━\n"
        f"/run_api_test — API тесты\n"
        f"/run_ui_test — UI тесты\n"
        f"/run_load_test — Нагрузочный тест",
        parse_mode='HTML',
        reply_markup=MAIN_MENU
    )


async def callback_last_report(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Обработчик кнопки 'Отчёт' — показать последний отчёт."""
    query = update.callback_query
    chat_id = query.message.chat_id
    await safe_answer(query)
    await cleanup_messages(
        context, chat_id, context.user_data,
        except_id=query.message.message_id
    )
    report_file = Path("./test_report.txt")
    if report_file.exists():
        content = report_file.read_text(encoding="utf-8")
        if len(content) > 3000:
            content = content[-3000:]
        await query.edit_message_text(
            f"📋 <b>Последний отчёт</b>\n{SEP}\n\n"
            f"<code>{content}</code>",
            parse_mode='HTML',
            reply_markup=MAIN_MENU
        )
    else:
        await query.edit_message_text(
            f"📋 <b>Последний отчёт</b>\n{SEP}\n\n"
            f"Отчёт пока не создан.\n"
            f"Запусти тесты и вернись снова!",
            parse_mode='HTML',
            reply_markup=MAIN_MENU
        )


async def callback_settings(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Обработчик кнопки 'Настройки' — показать настройки бота."""
    query = update.callback_query
    chat_id = query.message.chat_id
    await safe_answer(query)
    await cleanup_messages(
        context, chat_id, context.user_data,
        except_id=query.message.message_id
    )
    await query.edit_message_text(
        f"⚙️ <b>Настройки</b>\n{SEP}\n\n"
        f"━━━━ <b>Проект</b> ━━━━\n"
        f"🌐 Сайт: ado-shop.com\n"
        f"🤖 Бот: ADO Shop Bot\n"
        f"📂 Тесты: tests/api + tests/ui\n\n"
        f"━━━━ <b>Окружение</b> ━━━━\n"
        f"🐍 Python: 3.x\n"
        f"🧪 Фреймворк: Pytest\n"
        f"📊 Отчёт: Allure\n"
        f"🌐 Браузер: Chrome (headless)\n\n"
        f"━━━━ <b>Действия</b> ━━━━\n"
        f"🔄 /start — Перезапуск меню\n"
        f"❓ /help — Список команд",
        parse_mode='HTML',
        reply_markup=MAIN_MENU
    )


async def run_load_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Запуск нагрузочного теста по команде /run_load_test."""
    chat_id = update.effective_chat.id
    await cleanup_messages(context, chat_id, context.user_data)
    msg = await update.message.reply_text(
        '⚡ Запуск нагрузочного теста (~30 сек)...'
    )
    await track_message(context, chat_id, msg, context.user_data)
    from tests.load_tests.run_load_test import run_load_test
    # Запуск блокирующей функции в отдельном потоке через executor
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None, run_load_test, 10, 5, "30s"
    )
    text = result.get("error") or result.get(
        "text", "Нет данных"
    )
    msg = await update.message.reply_text(
        text, reply_markup=MAIN_MENU
    )
    await track_message(context, chat_id, msg, context.user_data)


async def callback_run_load(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Обработчик кнопки 'Нагрузочный тест' — запуск нагрузочного теста."""
    query = update.callback_query
    chat_id = query.message.chat_id
    await safe_answer(query)
    await cleanup_messages(
        context, chat_id, context.user_data,
        except_id=query.message.message_id
    )
    msg = await query.message.reply_text(
        '⚡ Запуск нагрузочного теста (~30 сек)...'
    )
    await track_message(context, chat_id, msg, context.user_data)
    from tests.load_tests.run_load_test import run_load_test
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None, run_load_test, 10, 5, "30s"
    )
    text = result.get("error") or result.get(
        "text", "Нет данных"
    )
    msg = await query.message.reply_text(text)
    await track_message(context, chat_id, msg, context.user_data)


async def help_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Обработчик команды /help — список доступных команд."""
    await update.message.reply_text(
        "📋 Доступные команды:\n\n"
        "/start — Главное меню с кнопками\n"
        "/help — Список команд\n"
        "/run_api_test — Запуск API тестов\n"
        "/run_ui_test — Запуск UI тестов\n"
        "/run_load_test — Нагрузочный тест\n"
        "/run_spell — Проверка орфографии\n"
        "/run_elements — Отображение элементов\n"
        "/run_business — Бизнес-сценарии\n\n"
        "Или нажми /start и выбери кнопку:"
    )


async def post_shutdown(application: Application) -> None:
    """Корректно закрывает HTTP-сессию бота при завершении."""
    await application.bot.shutdown()


def main() -> None:
    """Точка входа: настройка и запуск Telegram-бота."""
    acquire_lock()
    signal.signal(signal.SIGINT, release_lock)
    signal.signal(signal.SIGTERM, release_lock)

    application = (
        Application.builder()
        .token(os.getenv("TOKEN"))
        .post_shutdown(post_shutdown)
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(
        CommandHandler("run_api_test", run_api_command)
    )
    application.add_handler(
        CommandHandler("run_ui_test", run_ui_command)
    )
    application.add_handler(
        CommandHandler("run_load_test", run_load_command)
    )

    application.add_handler(
        CallbackQueryHandler(
            callback_run_api, pattern="^run_api$"
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            callback_run_ui, pattern="^run_ui$"
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            callback_run_load, pattern="^run_load$"
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            callback_about_me, pattern="^about_me$"
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            callback_about_site, pattern="^about_site$"
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            callback_run_links, pattern="^run_links$"
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            callback_about_ado, pattern="^about_ado$"
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            callback_ado_songs, pattern="^ado_songs$"
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            callback_back_to_main, pattern="^back_to_main$"
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            callback_run_spell, pattern="^run_spell$"
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            callback_run_elements, pattern="^run_elements$"
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            callback_run_business, pattern="^run_business$"
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            callback_run_all, pattern="^run_all$"
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            callback_stats, pattern="^stats$"
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            callback_last_report, pattern="^last_report$"
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            callback_settings, pattern="^settings$"
        )
    )

    try:
        application.run_polling(
            allowed_updates=Update.ALL_TYPES
        )
    finally:
        release_lock()


if __name__ == "__main__":
    main()
