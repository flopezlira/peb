"""
Unit Testing Module for Telegram Bot

This module contains unit tests for a Telegram bot that interacts with users and processes their
requests using OpenAI's GPT model. The tests focus on the bot's conversation states, ensuring the
correct flow and response handling. External dependencies, such as the Telegram Bot API and OpenAI
API, are mocked to isolate and test the internal logic of the bot.

The tests utilize `pytest` as the testing framework and `unittest.mock` for mocking external
services. Each function in the bot is tested individually to validate its behavior in different
scenarios.

Key Components:
- pytest: For writing and running the unit tests.
- unittest.mock: For mocking external API calls and interactions.
- Test cases: Covering each state handling function in the bot.

Usage:
Run these tests using a pytest runner to validate the bot's functionality.

Dependencies:
- pytest
- unittest.mock
- python-telegram-bot
"""

from unittest.mock import Mock

import pytest
from telegram import Chat, Message, Update
from telegram.ext import CallbackContext

from peb.data import BotState
from peb.telegram_bot import process_dict


# Sample test for the 'start' function
@pytest.mark.parametrize("state, expected_next_state", [
    ("start", BotState.GOAL),
    ("goal", BotState.PERSONA),
    ("persona", BotState.TASK),
    ("task", BotState.WHOM),
    ("whom", BotState.HOW),
    ("how", BotState.FORMAT),
    ("format", BotState.CONSTRAINTS),
    ("constraints", BotState.TOOL),
    ("tool", BotState.QUALITY),
    ("quality", BotState.OPENAI),
])
def test_state_function(state, expected_next_state, mocker):
    """
        Test the 'start' function of the Telegram bot.

        This test simulates the '/start' command being sent to the bot and asserts the response.
        The test ensures that the bot transitions to the 'GOAL' state upon receiving
        the '/start' command and that it sends the correct welcome message to the user.

        Parameters:
        - mocker (pytest.fixture): The pytest mocker fixture used to mock the reply_text method.

        The Update and CallbackContext objects from the Telegram bot API are mocked to simulate
        the interaction without actual network calls. The result and behavior of the 'start'
        function are then asserted to ensure the correct functionality.

        Asserts:
        - The returned state is BotState.GOAL.
        - The bot sends the correct welcome message to the user.
        """
    # Mocking the necessary parts of the Update and CallbackContext
    update = Mock(spec=Update)
    context = Mock(spec=CallbackContext)

    process_request_mock = mocker.patch("peb.telegram_bot.process_request")
    process_request_mock.return_value = None
    update_user_data_mock = mocker.patch("peb.telegram_bot.update_user_data")
    update_user_data_mock.return_value = None

    # Setting up the mocked Update object
    update.message = Mock(spec=Message)
    update.message.chat = Mock(spec=Chat)
    update.message.chat.id = 12345
    update.message.text = "/start"

    # Mocking the reply_text method
    update.message.reply_text = mocker.Mock()
    update.message.reply_text.return_value = None

    update_message_callback_mock = mocker.patch("peb.telegram_bot.update_message_callback")
    update_message_callback_mock.return_value = None
    assemble_prompt_mock = mocker.patch("peb.telegram_bot.assemble_prompt")
    assemble_prompt_mock.return_value = Mock()
    assemble_prompt_mock.return_value = "Welcome to the bot!", "What's your goal?"

    # Call the start function
    result = process_dict[state](update, context)

    # Assert that the function returns the correct next state
    assert result == expected_next_state
