import asyncio
from pathlib import Path
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters


async def execute_command(cmd: str, update:Update, timeout: int = 300) -> str:
    try:
        proc = await asyncio.create_subprocess_shell(cmd,
                                                     stdout=asyncio.subprocess.PIPE,
                                                     stderr=asyncio.subprocess.PIPE
                                                     )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout)
        output = f"STDOUT:\n{stdout.decode().strip()}" if stdout else ''
        output += f"\nSTDOUT:\n{stderr.decode().strip()}" if stderr else ''
        return output.strip()
    except asyncio.TimeoutError:
        return f"Таймаут {timeout} сек"
    except Exception as e:
        return f'Ошибка {str(e)}'


async def run_api_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Запуск тестов api')
    results_dir = Path("./results")
    results_dir.mkdir(exist_ok=True)

    for file in results_dir.glob("*"):
        file.unlink()

    result = await execute_command('pytest -s -v tests/api --alluredir=./results', update)

    short_result = '\n'. join([line for line in result.split('\n') if "FAILED" in line or "ERROR" in line])
    await update.message.reply_text(f"Результат тестов\n{short_result[:3000]}" if short_result else "Все тесты прошли успешно")


async def run_ui_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Запуск тестов api')
    results_dir = Path("./results")
    results_dir.mkdir(exist_ok=True)

    for file in results_dir.glob("*"):
        file.unlink()

    result = await execute_command('pytest -s -v tests/ui --alluredir=./results', update)

    short_result = '\n'. join([line for line in result.split('\n') if "FAILED" in line or "ERROR" in line])
    await update.message.reply_text(f"Результат тестов\n{short_result[:3000]}" if short_result else "Все тесты прошли успешно")


async def help_command2(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Как у вас дела!13213213")


async def help_command1(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Как у вас 3213213213214235634дела!")


def main() -> None:
    application = Application.builder().token("").build()
    application.add_handler(CommandHandler("test2", help_command2))
    application.add_handler(CommandHandler("test1", help_command1))
    application.add_handler(CommandHandler("run_api_test", run_api_test))
    application.add_handler(CommandHandler("run_ui_test", run_ui_test))
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
