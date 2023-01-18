"""This is a service bot for the developer team of the NoteD website."""
import telebot
from telebot import types

from config import TELEGRAM_TOKEN
from github import get_commits
from formatters import format_commit


bot = telebot.TeleBot(TELEGRAM_TOKEN)


@bot.message_handler(commands=["commits"])
def display_commits(message):
    """Sends last 5 commits with inline buttons.

    Displays commit information - comment, hash.
    Buttons:
        1. Url to the GitHub commit.
        future: [2. Starts a Jenkins job to build this commit.]
    """
    try:
        commits = get_commits()
    except Exception as error:
        bot.send_message(message.chat.id, "An error has occurred, try later.")
        print(error)
    for i, commit in enumerate(commits):
        commit_msg = format_commit(commit, nn=i + 1)
        kb = types.InlineKeyboardMarkup(row_width=2)
        kb.add(
            types.InlineKeyboardButton(text="Build", url=commit["url"]),
            types.InlineKeyboardButton(text="Details", url=commit["url"]),
        )
        bot.send_message(
            message.chat.id, commit_msg, parse_mode="HTML", reply_markup=kb
        )


@bot.message_handler(commands=["help"])
def send_help_info(message):
    """Sends information about the bot - (description, commands)."""
    bot.send_message(
        message.chat.id,
        "I am a service bot for the NoteD team.\n\n"
        + "Commands:\n"
        + "/commits - Display last 5 commits\n"
        + "/help - Bot information",
    )


bot.infinity_polling()
