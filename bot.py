"""This is a service bot for the developer team of the NoteD website."""
import telebot
from telebot import types

from config import TELEGRAM_TOKEN
from formatters import format_commit
from github import get_commits
from jenkins import build_noted_pipeline, build_stub_off


bot = telebot.TeleBot(TELEGRAM_TOKEN)


@bot.message_handler(commands=["commits"])
def display_commits(message):
    """Sends last 3 commits with inline buttons.

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
            types.InlineKeyboardButton(
                text="Build", callback_data="build_commit$%^" + commit["sha"]
            ),
            types.InlineKeyboardButton(text="Details", url=commit["url"]),
        )
        bot.send_message(
            message.chat.id, commit_msg, parse_mode="HTML", reply_markup=kb
        )


@bot.message_handler(commands=["stuboff"])
def stub_off(message):
    """Starts a jenkins job to set off a webite stub."""
    result = build_stub_off()
    if result == "build":
        bot.send_message(
            message.chat.id, f"Build for setting stub off has requested."
        )
    elif result == "building":
        bot.send_message(message.chat.id, "The job is currently building.")


@bot.message_handler(commands=["help"])
def send_help_info(message):
    """Sends information about the bot - (description, commands)."""
    bot.send_message(
        message.chat.id,
        "I am a service bot for the NoteD team.\n\n"
        + "Commands:\n"
        + "/commits - Display last 3 commits\n"
        + "/stuboff - Set the stub off\n"
        + "/help - Bot information",
    )


@bot.callback_query_handler(
    func=lambda cb: cb.data.split("$%^")[0] == "build_commit"
)
def build_commit(callback):
    commit_hash = callback.data.split("$%^")[1]
    result = build_noted_pipeline(commit_hash)
    if result == "build":
        bot.send_message(
            callback.message.chat.id, f"Build for {commit_hash} has requested."
        )
    elif result == "building":
        bot.send_message(
            callback.message.chat.id, "The job is currently building."
        )


bot.infinity_polling()
