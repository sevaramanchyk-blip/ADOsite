import asyncio
import os
import re
import sys
import signal
from pathlib import Path
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)

PID_FILE = Path(__file__).parent / ".bot.pid"


def acquire_lock():
    if PID_FILE.exists():
        old_pid = int(PID_FILE.read_text().strip())
        try:
            os.kill(old_pid, 0)
            print(
                f"Бот уже запущен (PID {old_pid}). "
                "Завершите предыдущий процесс."
            )
            sys.exit(1)
        except OSError:
            PID_FILE.unlink()
    PID_FILE.write_text(str(os.getpid()))


def release_lock(signum=None, frame=None):
    if PID_FILE.exists():
        PID_FILE.unlink()
    sys.exit(0)


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


def clear_results():
    results_dir = Path("./results")
    results_dir.mkdir(exist_ok=True)
    for file in results_dir.glob("*"):
        file.unlink()


def format_api_results(result: str) -> str:
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
    emoji = "✅" if not failed else "❌"

    table = f"<b>{emoji} API тесты — {len(passed)}/{total}</b>\n"
    table += f"<code>Пройдено: {len(passed)} | Провалено: {len(failed)} | Успешность: {success_rate:.0f}%</code>\n\n"

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
    emoji = "✅" if not failed else "❌"

    table = f"<b>{emoji} UI тесты — {len(passed)}/{total}</b>\n"
    table += f"<code>Пройдено: {len(passed)} | Провалено: {len(failed)} | Успешность: {success_rate:.0f}%</code>\n\n"

    if passed:
        table += "<b>Пройденные:</b>\n"
        for name in passed:
            table += f"  ✅ <code>{name}</code>\n"

    if failed:
        table += "\n<b>Проваленные:</b>\n"
        for name in failed:
            table += f"  ❌ <code>{name}</code>\n"

    return table


def format_load_results(result: str) -> str:
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
    emoji = "✅" if not failed else "❌"

    table = f"<b>{emoji} UI тесты — {len(passed)}/{total}</b>\n"
    table += f"<code>Пройдено: {len(passed)} | Провалено: {len(failed)} | Успешность: {success_rate:.0f}%</code>\n\n"

    if passed:
        table += "<b>Пройденные:</b>\n"
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
    await update.message.reply_text(
        "Привет! Я бот для запуска тестов ADO Shop.\n"
        "Выбери действие:",
        reply_markup=MAIN_MENU
    )


async def run_api_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text('⏳ Запуск API тестов...')
    clear_results()
    result = await execute_command(
        'pytest -s -v tests/api --alluredir=./results'
    )
    text = format_api_results(result)
    await update.message.reply_text(
        text or "✅ Все API тесты прошли успешно",
        parse_mode='HTML',
        reply_markup=MAIN_MENU
    )


async def run_ui_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text('⏳ Запуск UI тестов...')
    clear_results()
    result = await execute_command(
        'pytest -s -v tests/ui --alluredir=./results'
    )
    text = format_ui_results(result)
    await update.message.reply_text(
        text or "✅ Все UI тесты прошли успешно",
        parse_mode='HTML',
        reply_markup=MAIN_MENU
    )


async def callback_run_api(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("⏳ Запуск API тестов...")
    clear_results()
    result = await execute_command(
        'pytest -s -v tests/api --alluredir=./results'
    )
    text = format_api_results(result)
    await query.edit_message_text(
        text or "✅ Все API тесты прошли успешно",
        parse_mode='HTML',
        reply_markup=MAIN_MENU
    )


async def callback_run_ui(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("⏳ Запуск UI тестов...")
    clear_results()
    result = await execute_command(
        'pytest -s -v tests/ui --alluredir=./results'
    )
    text = format_ui_results(result)
    await query.edit_message_text(
        text or "✅ Все UI тесты прошли успешно",
        parse_mode='HTML',
        reply_markup=MAIN_MENU
    )


async def callback_about_me(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "Привет! Я QA-инженер.\n\n"
        "🔹 Автоматизирую тесты (API + UI)\n"
        "🔹 Python, Selenium, Pytest, Allure\n"
        "🔹 Telegram-бот для запуска тестов\n\n"
        "Проект: ADO Official Music Shop — "
        "тестирование интернет-магазина",
        reply_markup=MAIN_MENU
    )


async def callback_about_site(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🎵 ADO Official Music Shop\n"
        "https://ado-shop.com/\n\n"
        "Официальный магазин музыки и мерча "
        "японской исполнительницы Ado.\n\n"
        "🔹 Коллекции: Shinzou, Hibana, Zanmu\n"
        "🔹 Мерч: альбомы, футболки, аксессуары\n"
        "🔹 Платформа: Shopify\n"
        "🔹 Тестирование: API + UI автотесты",
        reply_markup=MAIN_MENU
    )


async def run_load_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        '⚡ Запуск нагрузочного теста (~30 сек)...'
    )
    from run_load_test import run_load_test
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None, run_load_test, 10, 5, "30s"
    )
    text = result.get("error") or result.get(
        "text", "Нет данных"
    )
    await update.message.reply_text(
        text, reply_markup=MAIN_MENU
    )


async def callback_run_load(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        '⚡ Запуск нагрузочного теста (~30 сек)...'
    )
    from run_load_test import run_load_test
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None, run_load_test, 10, 5, "30s"
    )
    text = result.get("error") or result.get(
        "text", "Нет данных"
    )
    await query.edit_message_text(
        text, reply_markup=MAIN_MENU
    )


async def help_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    await update.message.reply_text(
        "📋 Доступные команды:\n\n"
        "/start — Главное меню с кнопками\n"
        "/help — Список команд\n"
        "/run_api_test — Запуск API тестов\n"
        "/run_ui_test — Запуск UI тестов\n"
        "/run_load_test — Нагрузочный тест\n\n"
        "Или нажми /start и выбери кнопку:"
    )


def main() -> None:
    acquire_lock()
    signal.signal(signal.SIGINT, release_lock)
    signal.signal(signal.SIGTERM, release_lock)

    application = (
        Application.builder()
        .token("8656139643:AAH_yuxfSALLcRKLUAdz8KlxQjtT90ejhWE")
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

    try:
        application.run_polling(
            allowed_updates=Update.ALL_TYPES
        )
    finally:
        release_lock()


if __name__ == "__main__":
    main()
