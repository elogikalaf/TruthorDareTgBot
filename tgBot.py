#!/usr/bin/env python
# pylint: disable=unused-argument, import-error
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import json

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

NAME, GENDER, ADULT, COUPLE, CHALLENGE, GAME = range(6)

user_data_dict = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about their gender."""

    conversation_id = update.effective_chat.id
    user_data_dict[conversation_id] = {}


    await update.message.reply_text(
        "Hi! wanna play Truth or Dare?"
        "I have to ask you some questions though\n\n" 
        "what's your name?",
        reply_markup=ReplyKeyboardRemove(),
        ),

    return NAME 
async def name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about their gender."""

    user = update.message.from_user
    reply_keyboard = [["Boy", "Girl", "Other"]]

    conversation_id = update.effective_chat.id

    # Store the user's name in the user_data_dict
    user_data_dict[conversation_id][update.message.text] = {}

    # Store the user's name in context for next function uses
    context.user_data["name"] = update.message.text

    logger.info("name of %s: %s", user.first_name, update.message.text)

    await update.message.reply_text(
        "Hi! wanna play Truth or dare?"
        "I have to ask you some questions though\n\n" 
        "Are you a boy or a girl?",
        reply_markup=ReplyKeyboardMarkup(
        reply_keyboard, one_time_keyboard=True, input_field_placeholder="Boy or Girl or Other?"
        ),
    )

    return GENDER

async def gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks the age."""
    user = update.message.from_user
    logger.info("Gender of %s: %s", user.first_name, update.message.text)

    conversation_id = update.effective_chat.id

    # Get the User name from context
    name = context.user_data.get("name", "")

    await update.message.reply_text(
        "I see! Please tell me how old you are, ",
        reply_markup=ReplyKeyboardRemove(),
    )

    # Store the User's gender in it's own sub dict
    user_data_dict[conversation_id][name]["gender"] = update.message.text

    return ADULT

async def adult(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the age and asks for a relationship status."""
    user = update.message.from_user

    logger.info("age of %s: %s", user.first_name, update.message.text)

    conversation_id = update.effective_chat.id

    reply_keyboard = [["couple", "single"]]

    name = context.user_data.get("name", "")

    await update.message.reply_text(
        "now tell me if you're playing with a partner or not",
        reply_markup=ReplyKeyboardMarkup(
        reply_keyboard, one_time_keyboard=True, input_field_placeholder="coule or single"
        ),
    )
    user_data_dict[conversation_id][name]["age"] = update.message.text

    return COUPLE 

async def couple(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the relationship status and asks for the challenge type."""
    user = update.message.from_user
    logger.info("rel status of %s: %s", user.first_name, update.message.text)
    reply_keyboard = [['truth', 'dare']]

    conversation_id = update.effective_chat.id

    name = context.user_data.get("name", "")


    await update.message.reply_text(
        "Please choose between truth or dare",
        reply_markup=ReplyKeyboardMarkup(
        reply_keyboard, one_time_keyboard=True, input_field_placeholder="turth or dare"
        ),
    )
    user_data_dict[conversation_id][name]["couple"] = update.message.text

    return CHALLENGE 


async def challenge(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the raltionship status and asks the type of challenge."""
    user = update.message.from_user
    logger.info("challege of %s: %s", user.first_name, update.message.text)

    name = context.user_data.get("name", "")


    conversation_id = update.effective_chat.id

    user_data_dict[conversation_id][name]["challenge"] = update.message.text

    with open("user_info.txt", "w") as file:
        file.write(json.dumps(user_data_dict))

    await update.message.reply_text("yor information has been stored, press /done if you are are done!\n\n\n"
                                    "or enter the information of the next player.\n"
                                    "Hello! what's your name?")

    return NAME 

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("done")

    return GAME
async def game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """show the users"""
    result = ""

    conversation_id = update.effective_chat.id
    try:
        for name, info in user_data_dict[conversation_id].items():
            result += f"Name: {name}\n"
            for key, value in info.items():
                result += f"{key}: {value}\n"
            result += "\n"
    except Exception as err:
        print(err)

    await update.message.reply_text(result)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END




def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("token").build()

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name), CommandHandler("done", game),],
            GENDER: [MessageHandler(filters.Regex("^(Boy|Girl|Other)$"), gender)],
            COUPLE: [ MessageHandler(filters.TEXT & ~filters.COMMAND, couple)],
            ADULT: [MessageHandler(filters.TEXT & ~filters.COMMAND, adult)],
            CHALLENGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, challenge)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    while True:
        # Run the bot until the user presses Ctrl-C
        application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
