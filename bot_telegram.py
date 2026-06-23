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
from pathlib import Path
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
        except OSError:
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
])


async def execute_command(cmd: str, timeout: int = 300) -> str:
    """Выполняет shell-команду с таймаутом и возвращает stdout/stderr."""
    try:
        # Запускаем процесс с перехватом stdout и stderr
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(), timeout
        )
        # Формируем вывод: STDOUT + STDERR
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


def format_api_results(result: str) -> str:
    """Форматирует результаты API тестов в HTML-таблицу."""
    lines = result.split('\n')
    passed = []
    failed = []

    # Парсим вывод pytest: извлекаем имена тестов и их статусы
    for line in lines:
        if 'PASSED' in line or 'FAILED' in line:
            match = re.search(
                r'(.+?)\s+(PASSED|FAILED)', line
            )
            if match:
                name = match.group(1).strip()
                status = match.group(2)
                # Убираем префикс модуля (module::test_name -> test_name)
                if '::' in name:
                    name = name.split('::')[-1]
                if status == 'PASSED':
                    passed.append(name)
                else:
                    failed.append(name)

    total = len(passed) + len(failed)
    if total == 0:
        return None

    success_rate = len(passed) / total * 100

    # Формируем красивый отчёт с эмодзи и статистикой
    table = f"🚀 <b>API тесты</b> — {len(passed)}/{total}\n{SEP}\n"
    table += f"<code>✅ Пройдено: {len(passed)}\n"
    table += f"❌ Провалено: {len(failed)}\n"
    table += f"📊 Успешность: {success_rate:.0f}%</code>\n"

    if passed:
        table += "<b>Пройденные:</b>\n"
        for name in passed:
            short = name.split('[')[1].rstrip(']') if '[' in name else name
            table += f"  ✅ <code>{short}</code>\n"

    if failed:
        table += "\n<b>Проваленные:</b>\n"
        for name in failed:
            short = name.split('[')[1].rstrip(']') if '[' in name else name
            table += f"  ❌ <code>{short}</code>\n"

    return table


def format_ui_results(result: str) -> str:
    """Форматирует результаты UI тестов в HTML-таблицу."""
    lines = result.split('\n')
    passed = []
    failed = []

    for line in lines:
        if 'PASSED' in line or 'FAILED' in line:
            match = re.search(
                r'(.+?)\s+(PASSED|FAILED)', line
            )
            if match:
                name = match.group(1).strip()
                status = match.group(2)
                if '::' in name:
                    name = name.split('::')[-1]
                if status == 'PASSED':
                    passed.append(name)
                else:
                    failed.append(name)

    total = len(passed) + len(failed)
    if total == 0:
        return None

    success_rate = len(passed) / total * 100

    table = f"🌐 <b>UI тесты</b> — {len(passed)}/{total}\n{SEP}\n"
    table += f"<code>✅ Пройдено: {len(passed)}\n"
    table += f"❌ Провалено: {len(failed)}\n"
    table += f"📊 Успешность: {success_rate:.0f}%</code>\n"

    if passed:
        table += "\n<b>Пройденные:</b>\n"
        for name in passed:
            table += f"  ✅ <code>{name}</code>\n"

    if failed:
        table += "\n<b>Проваленные:</b>\n"
        for name in failed:
            table += f"  ❌ <code>{name}</code>\n"

    return table


def format_load_results(result: str) -> str:
    """Форматирует результаты нагрузочного теста в HTML-таблицу."""
    lines = result.split('\n')
    passed = []
    failed = []

    for line in lines:
        if 'PASSED' in line or 'FAILED' in line:
            match = re.search(
                r'(.+?)\s+(PASSED|FAILED)', line
            )
            if match:
                name = match.group(1).strip()
                status = match.group(2)
                if '::' in name:
                    name = name.split('::')[-1]
                if status == 'PASSED':
                    passed.append(name)
                else:
                    failed.append(name)

    total = len(passed) + len(failed)
    if total == 0:
        return None

    success_rate = len(passed) / total * 100

    table = f"⚡ <b>Нагрузочный тест</b> — {len(passed)}/{total}\n{SEP}\n"
    table += f"<code>✅ Пройдено: {len(passed)}\n"
    table += f"❌ Провалено: {len(failed)}\n"
    table += f"📊 Успешность: {success_rate:.0f}%</code>\n"

    if passed:
        table += "\n<b>Пройденные:</b>\n"
        for name in passed:
            table += f"  ✅ <code>{name}</code>\n"

    if failed:
        table += "\n<b>Проваленные:</b>\n"
        for name in failed:
            table += f"  ❌ <code>{name}</code>\n"

    return table


def format_results_generic(result: str, label: str, icon: str) -> str:
    """Универсальный форматировщик результатов тестов с настраиваемой подписью."""
    lines = result.split('\n')
    passed = []
    failed = []

    for line in lines:
        if 'PASSED' in line or 'FAILED' in line:
            match = re.search(
                r'(.+?)\s+(PASSED|FAILED)', line
            )
            if match:
                name = match.group(1).strip()
                status = match.group(2)
                if '::' in name:
                    name = name.split('::')[-1]
                if status == 'PASSED':
                    passed.append(name)
                else:
                    failed.append(name)

    total = len(passed) + len(failed)
    if total == 0:
        return None

    success_rate = len(passed) / total * 100

    table = f"{icon} <b>{label}</b> — {len(passed)}/{total}\n{SEP}\n"
    table += f"<code>✅ Пройдено: {len(passed)}\n"
    table += f"❌ Провалено: {len(failed)}\n"
    table += f"📊 Успешность: {success_rate:.0f}%</code>\n"

    if passed:
        table += "\n<b>Пройденные:</b>\n"
        for name in passed:
            table += f"  ✅ <code>{name}</code>\n"

    if failed:
        table += "\n<b>Проваленные:</b>\n"
        for name in failed:
            table += f"  ❌ <code>{name}</code>\n"

    return table


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
    """Запуск API тестов по команде /run_api_test."""
    chat_id = update.effective_chat.id
    await cleanup_messages(context, chat_id, context.user_data)
    msg = await update.message.reply_text('🚀 Запуск API тестов...')
    await track_message(context, chat_id, msg, context.user_data)
    clear_results()
    result = await execute_command(
        'pytest -s -v tests/api --alluredir=./results'
    )
    text = format_api_results(result)
    msg = await update.message.reply_text(
        text or "✅ Все API тесты прошли успешно!",
        parse_mode='HTML',
        reply_markup=MAIN_MENU
    )
    await track_message(context, chat_id, msg, context.user_data)


async def run_ui_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Запуск UI тестов по команде /run_ui_test."""
    chat_id = update.effective_chat.id
    await cleanup_messages(context, chat_id, context.user_data)
    msg = await update.message.reply_text('🌐 Запуск UI тестов...')
    await track_message(context, chat_id, msg, context.user_data)
    clear_results()
    result = await execute_command(
        'pytest -s -v tests/ui --alluredir=./results'
    )
    text = format_ui_results(result)
    msg = await update.message.reply_text(
        text or "✅ Все UI тесты прошли успешно!",
        parse_mode='HTML',
        reply_markup=MAIN_MENU
    )
    await track_message(context, chat_id, msg, context.user_data)


async def callback_run_api(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Обработчик кнопки 'API тесты' — запуск API тестов."""
    query = update.callback_query
    chat_id = query.message.chat_id
    # Удаляем старые сообщения бота, кроме текущего
    await cleanup_messages(
        context, chat_id, context.user_data,
        except_id=query.message.message_id
    )
    await query.answer()
    msg = await query.message.reply_text(
        "🚀 Запуск API тестов..."
    )
    await track_message(context, chat_id, msg, context.user_data)
    clear_results()
    result = await execute_command(
        'pytest -s -v tests/api --alluredir=./results'
    )
    text = format_api_results(result)
    msg = await query.message.reply_text(
        text or "✅ Все API тесты прошли успешно!",
        parse_mode='HTML'
    )
    await track_message(context, chat_id, msg, context.user_data)


async def callback_run_ui(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Обработчик кнопки 'UI тесты' — запуск UI тестов."""
    query = update.callback_query
    chat_id = query.message.chat_id
    await cleanup_messages(
        context, chat_id, context.user_data,
        except_id=query.message.message_id
    )
    await query.answer()
    msg = await query.message.reply_text(
        "🌐 Запуск UI тестов..."
    )
    await track_message(context, chat_id, msg, context.user_data)
    clear_results()
    result = await execute_command(
        'pytest -s -v tests/ui --alluredir=./results'
    )
    text = format_ui_results(result)
    msg = await query.message.reply_text(
        text or "✅ Все UI тесты прошли успешно!",
        parse_mode='HTML'
    )
    await track_message(context, chat_id, msg, context.user_data)


async def callback_run_spell(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Обработчик кнопки 'Орфография' — проверка орфографии на сайте."""
    query = update.callback_query
    chat_id = query.message.chat_id
    await cleanup_messages(
        context, chat_id, context.user_data,
        except_id=query.message.message_id
    )
    await query.answer()
    msg = await query.message.reply_text(
        "📝 Запуск проверки орфографии..."
    )
    await track_message(context, chat_id, msg, context.user_data)
    clear_results()
    result = await execute_command(
        'pytest -s -v tests/ui/test_spellcheck.py '
        '--alluredir=./results'
    )
    text = format_results_generic(
        result, "Проверка орфографии", "📝"
    )
    msg = await query.message.reply_text(
        text or "✅ Орфография в порядке!",
        parse_mode='HTML'
    )
    await track_message(context, chat_id, msg, context.user_data)


async def callback_run_elements(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Обработчик кнопки 'Элементы' — проверка отображения элементов."""
    query = update.callback_query
    chat_id = query.message.chat_id
    await cleanup_messages(
        context, chat_id, context.user_data,
        except_id=query.message.message_id
    )
    await query.answer()
    msg = await query.message.reply_text(
        "👁 Запуск проверки отображения элементов..."
    )
    await track_message(context, chat_id, msg, context.user_data)
    clear_results()
    result = await execute_command(
        'pytest -s -v tests/ui/test_elements.py '
        '--alluredir=./results'
    )
    text = format_results_generic(
        result, "Отображение элементов", "👁"
    )
    msg = await query.message.reply_text(
        text or "✅ Все элементы отображаются!",
        parse_mode='HTML'
    )
    await track_message(context, chat_id, msg, context.user_data)


async def callback_run_business(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Обработчик кнопки 'Сценарии' — запуск бизнес-сценариев."""
    query = update.callback_query
    chat_id = query.message.chat_id
    await cleanup_messages(
        context, chat_id, context.user_data,
        except_id=query.message.message_id
    )
    await query.answer()
    msg = await query.message.reply_text(
        "💼 Запуск бизнес-сценариев..."
    )
    await track_message(context, chat_id, msg, context.user_data)
    clear_results()
    result = await execute_command(
        'pytest -s -v tests/ui/test_business.py '
        '--alluredir=./results'
    )
    text = format_results_generic(
        result, "Бизнес-сценарии", "💼"
    )
    msg = await query.message.reply_text(
        text or "✅ Все сценарии пройдены!",
        parse_mode='HTML'
    )
    await track_message(context, chat_id, msg, context.user_data)


async def callback_about_ado(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Обработчик кнопки 'Про Ado' — показывает информацию об исполнителе."""
    query = update.callback_query
    chat_id = query.message.chat_id
    await cleanup_messages(
        context, chat_id, context.user_data,
        except_id=query.message.message_id
    )
    await query.answer()
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
    await cleanup_messages(
        context, chat_id, context.user_data,
        except_id=query.message.message_id
    )
    await query.answer()
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
    await query.answer()
    await query.edit_message_text(
        "Выбери действие 👇",
        reply_markup=MAIN_MENU
    )


async def callback_about_me(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Обработчик кнопки 'Обо мне' — информация о QA-инженере."""
    query = update.callback_query
    chat_id = query.message.chat_id
    await cleanup_messages(
        context, chat_id, context.user_data,
        except_id=query.message.message_id
    )
    await query.answer()
    await query.edit_message_text(
        f"👤 <b>Обо мне</b>\n{SEP}\n\n"
        f"QA-инженер 🔧\n\n"
        f"━━━━ <b>Навыки</b> ━━━━\n"
        f"🔹 Автоматизация тестов (API + UI)\n"
        f"🔹 Python, Selenium, Pytest, Allure\n"
        f"🔹 Telegram-боты\n\n"
        f"━━━━ <b>Проект</b> ━━━━\n"
        f"ADO Official Music Shop —\n"
        f"тестирование интернет-магазина 🛒",
        parse_mode='HTML',
        reply_markup=MAIN_MENU
    )


async def callback_about_site(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Обработчик кнопки 'Магазин ADO' — информация о сайте ado-shop.com."""
    query = update.callback_query
    chat_id = query.message.chat_id
    await cleanup_messages(
        context, chat_id, context.user_data,
        except_id=query.message.message_id
    )
    await query.answer()
    await query.edit_message_text(
        f"🛒 <b>ADO Official Music Shop</b>\n{SEP}\n"
        f"🌐 https://ado-shop.com/\n\n"
        f"Официальный магазин музыки и мерча\n"
        f"японской исполнительницы Ado 🎤\n\n"
        f"━━━━ <b>Каталог</b> ━━━━\n"
        f"💿 Коллекции: Shinzou, Hibana, Zanmu\n"
        f"👕 Мерч: альбомы, футболки, аксессуары\n\n"
        f"━━━━ <b>Технологии</b> ━━━━\n"
        f"💻 Платформа: Shopify\n"
        f"🧪 Тестирование: API + UI автотесты",
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
    from tests.load_test.run_load_test import run_load_test
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
    await cleanup_messages(
        context, chat_id, context.user_data,
        except_id=query.message.message_id
    )
    await query.answer()
    msg = await query.message.reply_text(
        '⚡ Запуск нагрузочного теста (~30 сек)...'
    )
    await track_message(context, chat_id, msg, context.user_data)
    from tests.load_test.run_load_test import run_load_test
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


def main() -> None:
    """Точка входа: настройка и запуск Telegram-бота."""
    acquire_lock()
    # Регистрируем обработчики сигналов для корректного завершения
    signal.signal(signal.SIGINT, release_lock)
    signal.signal(signal.SIGTERM, release_lock)

    # Создаём приложение бота с токеном из .env
    application = (
        Application.builder()
        .token(os.getenv("TOKEN"))
        .build()
    )

    # Регистрация командных обработчиков
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

    # Регистрация обработчиков инлайн-кнопок (callback-запросы)
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

    # Запуск бота в режиме long polling
    try:
        application.run_polling(
            allowed_updates=Update.ALL_TYPES
        )
    finally:
        release_lock()


if __name__ == "__main__":
    main()
