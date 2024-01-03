"""
This module implements a Telegram bot for interacting with users and processing their
requests using OpenAI's GPT model.
The bot guides users through a series of conversation states, collecting information
and responding accordingly.

It uses the Python Telegram Bot API to handle various types of updates and callback queries,
presenting users with a  range of options through inline keyboard buttons.
Each state in the conversation corresponds to a specific function,
which processes the user's input and determines the next state.

The bot integrates with OpenAI's GPT-3.5 model to generate and moderate content based on user input,
enhancing and  validating prompts to ensure they meet specific criteria.

Key Features:
- Multi-state conversation handling using the ConversationHandler from the Python Telegram Bot API.
- Dynamic inline keyboard button generation based on the current conversation state.
- Integration with OpenAI's GPT-3.5 model to create and moderate prompts.
- Extensive use of logging for debugging and tracking the flow of conversation.
- Environment variable management for secure storage of sensitive information like API keys.

The module is structured around the main function, which initializes the bot
and sets up the conversation handler and command handlers for starting and controlling
the flow of the conversation. Each conversation state is managed by a dedicated function,
and user data is stored and manipulated within the context of the conversation.

Dependencies:
- python-telegram-bot
- openai
- python-dotenv
"""

import logging
import os
from typing import Tuple

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    Filters,
    MessageHandler,
    Updater,
)

from peb.data import (
    BotState,
    final_message,
    state_code,
    state_examples,
    state_message,
    suggestions,
)
from peb.open_ai import OpenAI

load_dotenv()

MESSAGE = "Choose an option or enter your answer:"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def show_buttons(update, state) -> None:
    """
    Show buttons for the given state in the Telegram bot.

    Parameters:
    update (telegram.Update): The incoming update.
    context (telegram.ext.CallbackContext): The callback context provided by the Telegram bot.
    state (str): The current state of the bot to determine which buttons to show.

    Returns:
    None
    """
    logger.info("@Show buttons")
    logger.info("State: %s", state)
    if state not in ["start"]:
        keyboard = [[InlineKeyboardButton("🏠️ Start again", callback_data="start")]]
    if state not in ["start", "goal", "task", "persona", "openai", "whom"]:
        keyboard.append(
            [InlineKeyboardButton("⏩️ Skip this step ", callback_data=f"{state}")]
        )
    if state == "openai":
        keyboard.append(
            [InlineKeyboardButton("🧙‍♂️️ Perfect my prompt", callback_data="openai")]
        )
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        logger.info("Entering update message")
        update.message.reply_text(MESSAGE, reply_markup=reply_markup)
    elif update.callback_query:
        logger.info("Entering callback query")
        logger.info("Callback query: %s", update.callback_query)
        update.callback_query.message.reply_text(MESSAGE, reply_markup=reply_markup)
    else:
        logger.info("No update message or callback query")


def examples(state) -> str:
    """
    Generate a string of examples for a given state.

    Parameters:
    state (str): The state for which examples are needed.

    Returns:
    str: Formatted string containing examples.
    """
    return_str = "\n- ".join(state_examples[state])
    return f"Examples: \n- {return_str}"


def update_message_callback(update, message) -> None:
    """
    Send a message to the user based on the update type.

    Parameters:
    update (telegram.Update): The incoming update.
    context (telegram.ext.CallbackContext): The callback context provided by the Telegram bot.
    message (str): The message to be sent to the user.

    Returns:
    None
    """
    if update.message:
        update.message.reply_text(message)
    elif update.callback_query:
        update.callback_query.message.reply_text(message)


def start(update, context) -> BotState:
    """
    Start command for the Telegram bot.

    Parameters:
    update (telegram.Update): The incoming update.
    context (telegram.ext.CallbackContext): The callback context provided by the Telegram bot.

    Returns:
    BotState: The next state code.
    """
    logger.info("@Start")
    logger.info("Context user data 1: %s", context.user_data)
    context.user_data.clear()
    logger.info("Context user data 2: %s", context.user_data)
    logger.info("Context: %s", context)
    update_message_callback(update, f"{'. '.join(state_message[BotState.START])}")
    update_message_callback(update, f"{'. '.join(state_message[BotState.GOAL])}")
    update_message_callback(update, examples(BotState.GOAL))
    show_buttons(update, "goal")
    return BotState.GOAL


def update_user_data(update, context, key) -> None:
    """
    Update user data based on the message or callback query.

    Parameters:
    update (telegram.Update): The incoming update.
    context (telegram.ext.CallbackContext): The callback context provided by the Telegram bot.
    key (str): The key in user data to update.

    Returns:
    None
    """
    if update.message:
        context.user_data[key] = update.message.text
    elif update.callback_query:
        if update.callback_query.message.text == MESSAGE:
            context.user_data[key] = "None"
        else:
            context.user_data[key] = update.callback_query.message.text


def process_request(state, update, context, next_state, next_state_code) -> None:
    """
    Process the request for a given state and move to the next state.

    Parameters:
    state (str): The current state.
    update (telegram.Update): The incoming update.
    context (telegram.ext.CallbackContext): The callback context provided by the Telegram bot.
    next_state (str): The next state to transition to.
    next_state_code (str): The code of the next state.

    Returns:
    None
    """
    logger.info("@ %s", state)
    update_user_data(update, context, state)
    update_message_callback(update, f"{'. '.join(state_message[next_state])}")
    update_message_callback(update, examples(next_state))
    show_buttons(update, next_state_code)


def goal(update, context) -> BotState:
    """
    Handle the 'goal' state of the conversation.

    Parameters:
    update (telegram.Update): The incoming update.
    context (telegram.ext.CallbackContext): The callback context provided by the Telegram bot.

    Returns:
    BotState: The next state code.
    """
    process_request("goal", update, context, BotState.PERSONA, "persona")
    return BotState.PERSONA


def persona(update, context) -> BotState:
    """
    Handle the 'persona' state of the conversation.

    Parameters:
    update (telegram.Update): The incoming update.
    context (telegram.ext.CallbackContext): The callback context provided by the Telegram bot.

    Returns:
    BotState: The next state code.
    """
    process_request("persona", update, context, BotState.TASK, "task")
    return BotState.TASK


def task(update, context) -> BotState:
    """
    Handle the 'task' state of the conversation.

    Parameters:
    update (telegram.Update): The incoming update.
    context (telegram.ext.CallbackContext): The callback context provided by the Telegram bot.

    Returns:
    BotState: The next state code.
    """
    process_request("task", update, context, BotState.WHOM, "whom")
    return BotState.WHOM


def whom(update, context) -> BotState:
    """
    Handle the 'whom' state of the conversation.

    Parameters:
    update (telegram.Update): The incoming update.
    context (telegram.ext.CallbackContext): The callback context provided by the Telegram bot.

    Returns:
    BotState: The next state code.
    """
    process_request("whom", update, context, BotState.HOW, "how")
    return BotState.HOW


def how(update, context) -> BotState:
    """
    Handle the 'how' state of the conversation.

    Parameters:
    update (telegram.Update): The incoming update.
    context (telegram.ext.CallbackContext): The callback context provided by the Telegram bot.

    Returns:
    BotState: The next state code.
    """
    process_request("how", update, context, BotState.FORMAT, "format")
    return BotState.FORMAT


def formatting(update, context) -> BotState:
    """
    Handle the 'format' state of the conversation.

    Parameters:
    update (telegram.Update): The incoming update.
    context (telegram.ext.CallbackContext): The callback context provided by the Telegram bot.

    Returns:
    BotState: The next state code.
    """
    process_request("format", update, context, BotState.CONSTRAINTS, "constraints")
    return BotState.CONSTRAINTS


def assemble_prompt(context) -> Tuple[str, str]:
    """
    Assemble the prompt based on the user's input collected in various stages.

    Parameters:
    context (telegram.ext.CallbackContext): The callback context containing user data.

    Returns:
    tuple: A tuple containing the summary and enhancement based on user data.
    """
    summary = ""
    enhancement = ""
    logger.info("User data: %s", context.user_data)
    for stage, message in final_message.items():
        if stage in context.user_data:
            user_data_value = context.user_data[stage]
            if user_data_value not in ["None", MESSAGE]:
                summary += f"{message} {user_data_value}\n"
            else:
                if stage in suggestions:
                    enhancement += f"{suggestions[stage]}\n"
    logger.info("Summary: %s", summary)
    logger.info("Enhancement: %s", enhancement)
    return summary, enhancement


def constraints(update, context) -> BotState:
    """
    Handle the 'constraints' state of the conversation.

    Parameters:
    update (telegram.Update): The incoming update.
    context (telegram.ext.CallbackContext): The callback context provided by the Telegram bot.

    Returns:
    BotState: The next state code.
    """
    process_request("constraints", update, context, BotState.TOOL, "tool")
    return BotState.TOOL


def tool(update, context) -> BotState:
    """
    Handle the 'tool' state of the conversation.

    Parameters:
    update (telegram.Update): The incoming update.
    context (telegram.ext.CallbackContext): The callback context provided by the Telegram bot.

    Returns:
    BotState: The next state code.
    """
    process_request("tool", update, context, BotState.QUALITY, "quality")
    return BotState.QUALITY


def quality(update, context) -> BotState:
    """
    Handle the 'quality' state of the conversation.

    Parameters:
    update (telegram.Update): The incoming update.
    context (telegram.ext.CallbackContext): The callback context provided by the Telegram bot.

    Returns:
    BotState: The next state code.
    """
    logger.info("@Quality")
    update_user_data(update, context, "quality")
    update_message_callback(update, "This is your request in draft form:\n")
    prompt, _ = assemble_prompt(context)
    if not prompt:
        if update.message:
            update.message.reply_text("Something went wrong. Please try again.")
        return BotState.START
    update_message_callback(update, prompt)
    show_buttons(update, "openai")
    return BotState.OPENAI


def open_ai(update, context) -> None:
    """
    Handle the 'openai' state and process the request through OpenAI API.

    Parameters:
    update (telegram.Update): The incoming update.
    context (telegram.ext.CallbackContext): The callback context provided by the Telegram bot.

    Returns:
    int: The next state code or ends the conversation.
    """
    logger.info("@OpenAI")
    logger.info(context.user_data)
    context.user_data["openai"] = "OpenAI"
    openai_obj = OpenAI()

    prompt, enhancement = assemble_prompt(context)
    logger.info("Prompt: %s", prompt)
    success, err_msg, banned_content = openai_obj.moderate(prompt)
    if not success:
        logger.info("Error: %s", err_msg)
        update_message_callback(update, err_msg)
        return
    if banned_content:
        logger.info("Banned content")
        update_message_callback(
            update,
            "Your prompt contains banned content and it cannot be processed.",
        )
        return
    success, err_msg, response = openai_obj.create(
        instruction=openai_obj.prompt_enhancement_instruction,
        prompt=prompt,
        enhancement=enhancement,
    )
    if not success:
        logger.info("Error: %s", err_msg)
        update_message_callback(update, err_msg)
        return
    logger.info("Response: %s", response)
    response_text = response.choices[0].message.content
    logger.info("Response text: %s", response_text)
    explaining_text = (
        "This is your prompt enhanced. You can copy it and paste it in ChatGPT."
    )
    update_message_callback(update, explaining_text)
    update_message_callback(update, response_text)


process_dict = {
    "start": start,
    "goal": goal,
    "persona": persona,
    "task": task,
    "whom": whom,
    "how": how,
    "format": formatting,
    "constraints": constraints,
    "tool": tool,
    "quality": quality,
    "openai": open_ai,
}


def get_curr_state(update) -> str:
    """
    Get the current state from the update object.

    Parameters:
    update (Update): The incoming update from the Telegram API.

    Returns:
    str: The current state extracted from the update's callback data.
    """
    if update.callback_query:
        query = update.callback_query
    if update.message:
        query = update.message
    callback_data = query.data.split("_")
    current_state = callback_data[0]
    return current_state


def button(update, context) -> BotState:
    """
    Handle button press in the Telegram bot.

    Parameters:
    update (Update): The incoming update from the Telegram API.
    context (CallbackContext): The callback context provided by the Telegram bot.

    Returns:
    BotState: The code of the next state in the conversation.
    """
    logger.info("@Button")
    query = update.callback_query
    query.answer()
    callback_data = query.data.split("_")
    current_state = callback_data[0]
    logger.info("Call back data: %s", str(callback_data))
    logger.info("Current state: %s", current_state)
    processes_with_buttons = [
        "how",
        "format",
        "constraints",
        "tool",
        "quality",
        "openai",
    ]
    if current_state in processes_with_buttons:
        logger.info("Entering %s", current_state)
        process_dict[current_state](update, context)
        return state_code[current_state]
    if current_state == "start":
        logger.info("Entering start again")
        callback_data[0] = "goal"
        start(update, context)
        return BotState.START
    return state_code[current_state + 1]


def main():
    """
    Main function to start the Telegram bot.

    Initializes the bot, sets up the conversation handler, and starts polling for updates.

    Returns:
    None
    """
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    # Initialize the Updater
    updater = Updater(telegram_token, use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start), CommandHandler("cancel", start)],
        states={
            BotState.START: [MessageHandler(Filters.text & ~Filters.command, start)],
            BotState.GOAL: [MessageHandler(Filters.text & ~Filters.command, goal)],
            BotState.PERSONA: [
                MessageHandler(Filters.text & ~Filters.command, persona)
            ],
            BotState.TASK: [MessageHandler(Filters.text & ~Filters.command, task)],
            BotState.WHOM: [MessageHandler(Filters.text & ~Filters.command, whom)],
            BotState.HOW: [MessageHandler(Filters.text & ~Filters.command, how)],
            BotState.FORMAT: [
                MessageHandler(Filters.text & ~Filters.command, formatting)
            ],
            BotState.CONSTRAINTS: [
                MessageHandler(Filters.text & ~Filters.command, constraints)
            ],
            BotState.TOOL: [MessageHandler(Filters.text & ~Filters.command, tool)],
            BotState.QUALITY: [
                MessageHandler(Filters.text & ~Filters.command, quality)
            ],
            BotState.OPENAI: [MessageHandler(Filters.text & ~Filters.command, open_ai)],
        },
        fallbacks=[CommandHandler("cancel", start)],
    )
    dp.add_handler(conv_handler)
    dp.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
