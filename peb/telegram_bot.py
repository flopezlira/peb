import logging
import os

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    Filters,
    MessageHandler,
    PreCheckoutQueryHandler,
    Updater,
)

from data import *
from open_ai import OpenAI

load_dotenv()

MESSAGE = "Choose an option or enter your answer:"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def get_next_state(current_state):
    next_state = state_code[current_state] + 1
    for key, value in state_code.items():
        if value == next_state:
            next_state = key
            break
    return next_state


def show_buttons(update, context, state):
    logger.info("@Show buttons")
    logger.info("State: %s", state)
    if state not in ["start"]:
        keyboard = [[InlineKeyboardButton("🏠️ Start again", callback_data="start")]]
    if state not in ["start", "goal", "task", "persona", "payment", "openai", "whom"]:
        keyboard.append(
            [InlineKeyboardButton(f"⏩️ Skip this step ", callback_data=f"{state}")]
        )
    if state == "openai":
        keyboard.append(
            [InlineKeyboardButton("🧙‍♂️️ Perfect my prompt", callback_data="openai")]
        )
    # if state == "payment":
    #     keyboard.append(
    #         [
    #             InlineKeyboardButton(
    #                 " 😀️ Happy? Buy me a coffe! ☕️", callback_data="payment"
    #             )
    #         ]
    #     )
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


def examples(state):
    return_str = "\n- ".join(state_examples[state])
    return f"Examples: \n- {return_str}"


def update_message_callback(update, context, message):
    if update.message:
        update.message.reply_text(message)
    elif update.callback_query:
        update.callback_query.message.reply_text(message)


def start(update, context):
    logger.info("@Start")
    logger.info("Context user data 1: %s", context.user_data)
    context.user_data.clear()
    c = "goal"
    logger.info("Context user data 2: %s", context.user_data)
    logger.info("Context: %s", context)
#    logger.info('Current state %s', get_curr_state(update, context))
    update_message_callback(update, context, f"{'. '.join(state_message[START])}")
    update_message_callback(update, context, f"{'. '.join(state_message[GOAL])}")
    update_message_callback(update, context, examples(GOAL))
    show_buttons(update, context, "goal")
    return GOAL


def update_user_data(update, context, key):
    if update.message:
        context.user_data[key] = update.message.text
    elif update.callback_query:
        if update.callback_query.message.text == MESSAGE:
            context.user_data[key] = "None"
        else:
            context.user_data[key] = update.callback_query.message.text


def process_request(state, update, context, next_state, next_state_code):
    logger.info("@ %s", state)
    update_user_data(update, context, state)
    update_message_callback(update, context, f"{'. '.join(state_message[next_state])}")
    update_message_callback(update, context, examples(next_state))
    show_buttons(update, context, next_state_code)


def goal(update, context):
    process_request("goal", update, context, PERSONA, "persona")
    return PERSONA


def persona(update, context):
    process_request("persona", update, context, TASK, "task")
    return TASK


def task(update, context):
    process_request("task", update, context, WHOM, "whom")
    return WHOM


def whom(update, context):
    process_request("whom", update, context, HOW, "how")
    return HOW


def how(update, context):
    process_request("how", update, context, FORMAT, "format")
    return FORMAT


def formatting(update, context):
    process_request("format", update, context, CONSTRAINTS, "constraints")
    return CONSTRAINTS


def assemble_prompt(context):
    summary = ""
    enhancement = ""
    logger.info("User data: %s", context.user_data)
    for stage in final_message:
        if stage in context.user_data:
            if context.user_data[stage] not in ["None", MESSAGE]:
                summary += f"{final_message[stage]} {context.user_data[stage]}\n"
            else:
                if stage in suggestions:
                    enhancement += f"{suggestions[stage]}\n"
    logger.info("Summary: %s", summary)
    logger.info("Enhancement: %s", enhancement)
    return summary, enhancement


def constraints(update, context):
    process_request("constraints", update, context, TOOL, "tool")
    return TOOL


def tool(update, context):
    process_request("tool", update, context, QUALITY, "quality")
    return QUALITY


def quality(update, context):
    logger.info("@Quality")
    update_user_data(update, context, "quality")
    update_message_callback(update, context, f"This is your request in draft form:\n")
    prompt, _ = assemble_prompt(context)
    if not prompt:
        if update.message:
            update.message.reply_text("Something went wrong. Please try again.")
        return START
    update_message_callback(update, context, prompt)
    show_buttons(update, context, "openai")
    return OPENAI


def payment(update, context):
    logger.info("@Payment")
    if update.message:
        update.message.reply_text("Processing your payment...")
    product, price_data = fetch_stripe_product(PRODUCT_ID)
    logger.info("Product: %s", product)
    logger.info("Price data: %s", price_data)
    if update.message:
        logger.info("Chat id: %s", update.message.chat_id)
        send_invoice(update.message.chat_id, STRIPE_TEST, product, price_data)
    elif update.callback_query:
        logger.info("Chat id: %s", update.callback_query.message.chat_id)
        send_invoice(
            update.callback_query.message.chat_id, STRIPE_TEST, product, price_data
        )


def precheckout_callback(update, context):
    query = update.pre_checkout_query
    if query.invoice_payload != "some_payload":
        context.bot.answer_pre_checkout_query(
            pre_checkout_query_id=query.id,
            ok=False,
            error_message="Something went wrong...",
        )
    else:
        context.bot.answer_pre_checkout_query(pre_checkout_query_id=query.id, ok=True)


def successful_payment_callback(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="Thank you for your payment!"
    )


def open_ai(update, context):
    logger.info("@OpenAI")
    logger.info(context.user_data)
    context.user_data["openai"] = "OpenAI"
    openai_obj = OpenAI()

    prompt, enhancement = assemble_prompt(context)
    logger.info("Prompt: %s", prompt)
    banned_content = openai_obj.moderate(prompt)
    logger.info("Moderation response: %s", banned_content)
    logger.info("Moderation response: %s", type(banned_content))
    if banned_content:
        logger.info("Banned content")
        update_message_callback(
            update,
            context,
            "Your prompt contains banned content and it cannot be processed.",
        )
        return ConversationHandler.END
    response = openai_obj.create(
        instruction=openai_obj.PROMPT_ENHANCEMENT_INSTRUCTION,
        prompt=prompt,
        enhancement=enhancement,
    )
    logger.info("Response: %s", response)
    response_text = response["choices"][0]["message"]["content"]
    logger.info("Response text: %s", response_text)
    explaining_text = (
        "This is your prompt enhanced. You can copy it and paste it in ChatGPT."
    )
    update_message_callback(update, context, explaining_text)
    update_message_callback(update, context, response_text)
    show_buttons(update, context, "payment")
    return PAYMENT


def err_openai(update, context):
    update.message.reply_text("Please enter your OpenAI API key again.")
    show_buttons(update, context, "openai")
    return OPENAI


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
    "payment": payment,
    "openai": open_ai,
}


def get_curr_state(update, context):
    if update.callback_query:
        query = update.callback_query
    if update.message:
        query = update.message
    #query.answer()
    callback_data = query.data.split("_")
    current_state = callback_data[0]
    return current_state


def button(update, context):
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
        "payment",
        "openai",
    ]
    if current_state in processes_with_buttons:
        logger.info("Entering %s", current_state)
        process_dict[current_state](update, context)
        return state_code[current_state]
    if current_state == "start":
        logger.info("Entering start again")
        ConversationHandler.END
        callback_data[0] = "goal"
        start(update, context)
        return START


def main():
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    # Initialize the Updater
    updater = Updater(telegram_token, use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start), CommandHandler("cancel", start)],
        states={
            START: [MessageHandler(Filters.text & ~Filters.command, start)],
            GOAL: [MessageHandler(Filters.text & ~Filters.command, goal)],
            PERSONA: [MessageHandler(Filters.text & ~Filters.command, persona)],
            TASK: [MessageHandler(Filters.text & ~Filters.command, task)],
            WHOM: [MessageHandler(Filters.text & ~Filters.command, whom)],
            HOW: [MessageHandler(Filters.text & ~Filters.command, how)],
            FORMAT: [MessageHandler(Filters.text & ~Filters.command, formatting)],
            CONSTRAINTS: [MessageHandler(Filters.text & ~Filters.command, constraints)],
            TOOL: [MessageHandler(Filters.text & ~Filters.command, tool)],
            QUALITY: [MessageHandler(Filters.text & ~Filters.command, quality)],
            PAYMENT: [MessageHandler(Filters.text & ~Filters.command, payment)],
            OPENAI: [MessageHandler(Filters.text & ~Filters.command, open_ai)],
        },
        fallbacks=[CommandHandler("cancel", start)],
    )
    dp.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    dp.add_handler(
        MessageHandler(Filters.successful_payment, successful_payment_callback)
    )
    dp.add_handler(conv_handler)
    dp.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
