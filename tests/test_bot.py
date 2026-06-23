import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from telegram import Update, CallbackQuery, Message, Chat
from telegram.ext import ContextTypes


@pytest.fixture
def update():
    update = MagicMock(spec=Update)
    update.message = MagicMock(spec=Message)
    update.message.reply_text = AsyncMock()
    update.message.chat = MagicMock(spec=Chat)
    update.message.chat.id = 123
    return update


@pytest.fixture
def callback_update():
    update = MagicMock(spec=Update)
    query = MagicMock(spec=CallbackQuery)
    query.answer = AsyncMock()
    query.edit_message_text = AsyncMock()
    query.data = ""
    query.message = MagicMock()
    query.message.reply_text = AsyncMock()
    query.message.chat_id = 123
    query.message.message_id = 1
    update.callback_query = query
    return update


@pytest.fixture
def context():
    ctx = MagicMock()
    ctx.user_data = {}
    ctx.bot.delete_message = AsyncMock()
    return ctx


class TestHelpers:
    def test_clear_results(self, tmp_path):
        from bot_telegram import clear_results
        with patch("bot_telegram.Path") as MockPath:
            mock_dir = MagicMock()
            MockPath.return_value = mock_dir
            mock_dir.glob.return_value = []
            clear_results()
            mock_dir.mkdir.assert_called_once_with(exist_ok=True)

    def test_format_api_results_success(self):
        from bot_telegram import format_api_results
        result = "tests/test.py::test_one PASSED\ntests/test.py::test_two PASSED"
        text = format_api_results(result)
        assert "2/2" in text
        assert "✅" in text

    def test_format_api_results_failure(self):
        from bot_telegram import format_api_results
        result = "tests/test.py::test_one FAILED\nERROR in test"
        text = format_api_results(result)
        assert text is not None
        assert "❌" in text

    def test_format_ui_results_success(self):
        from bot_telegram import format_ui_results
        result = "tests/test_ui.py::test_links5 PASSED"
        text = format_ui_results(result)
        assert "1/1" in text
        assert "✅" in text


class TestStartCommand:
    @pytest.mark.asyncio
    async def test_start_replies_with_menu(self, update, context):
        from bot_telegram import start
        await start(update, context)
        update.message.reply_text.assert_called_once()
        call_args = update.message.reply_text.call_args
        assert "Выбери действие" in call_args[0][0]
        assert call_args[1]["reply_markup"] is not None


class TestHelpCommand:
    @pytest.mark.asyncio
    async def test_help_replies(self, update, context):
        from bot_telegram import help_command
        await help_command(update, context)
        update.message.reply_text.assert_called_once()
        text = update.message.reply_text.call_args[0][0]
        assert "/start" in text
        assert "/help" in text
        assert "/run_api_test" in text
        assert "/run_ui_test" in text


class TestCallbackAboutMe:
    @pytest.mark.asyncio
    async def test_about_me(self, callback_update, context):
        from bot_telegram import callback_about_me
        callback_update.callback_query.data = "about_me"
        await callback_about_me(callback_update, context)
        callback_update.callback_query.answer.assert_called_once()
        text = callback_update.callback_query.edit_message_text.call_args[0][0]
        assert "QA-инженер" in text


class TestCallbackAboutSite:
    @pytest.mark.asyncio
    async def test_about_site(self, callback_update, context):
        from bot_telegram import callback_about_site
        callback_update.callback_query.data = "about_site"
        await callback_about_site(callback_update, context)
        callback_update.callback_query.answer.assert_called_once()
        text = callback_update.callback_query.edit_message_text.call_args[0][0]
        assert "ado-shop.com" in text
        assert "Ado" in text


class TestRunApiCommand:
    @pytest.mark.asyncio
    async def test_run_api_command(self, update, context):
        from bot_telegram import run_api_command
        with patch("bot_telegram.execute_command", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = "tests/test.py PASSED"
            await run_api_command(update, context)
            mock_exec.assert_called_once()
            assert update.message.reply_text.call_count == 2


class TestRunUiCommand:
    @pytest.mark.asyncio
    async def test_run_ui_command(self, update, context):
        from bot_telegram import run_ui_command
        with patch("bot_telegram.execute_command", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = "tests/test.py PASSED"
            await run_ui_command(update, context)
            mock_exec.assert_called_once()
            assert update.message.reply_text.call_count == 2


class TestCallbackRunApi:
    @pytest.mark.asyncio
    async def test_callback_run_api(self, callback_update, context):
        from bot_telegram import callback_run_api
        callback_update.callback_query.data = "run_api"
        with patch("bot_telegram.execute_command", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = "tests/test.py PASSED"
            await callback_run_api(callback_update, context)
            callback_update.callback_query.answer.assert_called_once()
            assert callback_update.callback_query.message.reply_text.call_count == 2


class TestCallbackRunUi:
    @pytest.mark.asyncio
    async def test_callback_run_ui(self, callback_update, context):
        from bot_telegram import callback_run_ui
        callback_update.callback_query.data = "run_ui"
        with patch("bot_telegram.execute_command", new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = "tests/test.py PASSED"
            await callback_run_ui(callback_update, context)
            callback_update.callback_query.answer.assert_called_once()
            assert callback_update.callback_query.message.reply_text.call_count == 2


class TestExecuteCommand:
    @pytest.mark.asyncio
    async def test_execute_command_success(self):
        from bot_telegram import execute_command
        result = await execute_command("echo hello")
        assert "hello" in result

    @pytest.mark.asyncio
    async def test_execute_command_timeout(self):
        from bot_telegram import execute_command
        result = await execute_command("python -c \"import time; time.sleep(10)\"", timeout=1)
        assert "Таймаут" in result

    @pytest.mark.asyncio
    async def test_execute_command_error(self):
        from bot_telegram import execute_command
        result = await execute_command("python -c \"raise ValueError('test error')\"")
        assert "test error" in result or "Ошибка" in result


class TestLoadTest:
    def test_run_load_test(self):
        from load_tests.run_load_test import run_load_test
        result = run_load_test(users=1, spawn_rate=1, run_time="5s")
        assert "error" in result or "text" in result

    def test_parse_results_no_csv(self, tmp_path):
        from load_tests.run_load_test import parse_results
        result = parse_results(tmp_path / "nonexistent.csv", "")
        assert "error" in result
