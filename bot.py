"""This is a service bot for the developer team of the NoteD website.

The bot sends all messages to specific chat to make them secure.  
"""
import functools
import os

import telebot
from telebot import types

from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID as CHAT_ID
from formatters import format_commit
from github import get_commits, create_issue as create_issue_api
from jenkins import build_noted_pipeline, build_stub_off


TEXT_MESSAGES = {
    "welcome": str(
        "Welcome to NoteD Service Bot!\n\n"
        "The telegram bot provides the NoteD developer team with services "
        + "to help them manage developing processes and get developing "
        + "information. Provides requests to GitHub and Jenkins."
    ),
    "help": str(
        "I am a service bot for the NoteD team.\n\n"
        "I can help with:\n"
        "1. List last commits and build them to prodaction.\n"
        "2. Create issues to the project.\n"
        "3. Set off the stub of the website.\n\n"
        "Commands:\n"
        "/commits - Display last 3 commits\n"
        "/issue - Create an issue\n"
        "/stuboff - Set the stub off\n"
        "/help - Bot information"
    ),
    "wrong_chat": str(
        "Hi there!\n"
        "Thanks for trying me out. However, this bot can only be "
        + "used in the NoteD developer group chat.\n\n"
        "Check out our profect!\n"
        "https://welel-noted.site/"
    ),
}


if "TELEGRAM_TOKEN" not in os.environ or "TELEGRAM_CHAT_ID" not in os.environ:
    raise AssertionError(
        "Please configure TELEGRAM_TOKEN and TELEGRAM_CHAT_ID as environment variables"
    )

bot = telebot.TeleBot(TELEGRAM_TOKEN)


def is_api_group(chat_id: int) -> bool:
    """Check is a chat id equals to the team group chat id."""
    return chat_id == CHAT_ID


def check_group_chat(fn):
    """Decorates message handlers for checking the message chat id.

    If a message chat id is not the team group chat id then send warning.
    """

    @functools.wraps(fn)
    def wrapper(message, *args, **kwargs):
        if is_api_group(message.chat.id):
            return fn(message, *args, **kwargs)
        else:
            bot.send_message(message.chat.id, TEXT_MESSAGES["wrong_chat"])

    return wrapper


@bot.message_handler(commands=["start"])
def welcome(message):
    bot.send_message(message.chat.id, TEXT_MESSAGES["welcome"])
    if not is_api_group(message.chat.id):
        bot.send_message(message.chat.id, TEXT_MESSAGES["wrong_chat"])


@bot.message_handler(commands=["commits"])
@check_group_chat
def display_commits(message):
    """Sends last 3 commits with inline buttons.

    Displays commit information - comment, hash.
    Buttons:
        1. Url to the GitHub commit.
        2. Starts a Jenkins job to build this commit in the prodaction.
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
            CHAT_ID, commit_msg, parse_mode="HTML", reply_markup=kb
        )


@bot.callback_query_handler(
    func=lambda cb: cb.data.split("$%^")[0] == "build_commit"
)
def build_commit_handler(callback):
    """Handles the `Build` button of a comment, starts the Jenkins job.

    If a `Build` button was pressed starts the Jenkins job that builds
    the provided commit to the prodaction.
    """
    commit_hash = callback.data.split("$%^")[1]
    result = build_noted_pipeline(commit_hash)
    if result == "build":
        bot.send_message(CHAT_ID, f"Build for {commit_hash} has requested.")
    elif result == "building":
        bot.send_message(CHAT_ID, "The job is currently building.")


@bot.message_handler(commands=["issue"])
@check_group_chat
def create_issue(message):
    """Starts dialog for creating an issue to the GitHub repository."""
    sent_msg = bot.send_message(message.chat.id, "Write an issue title...")
    bot.register_next_step_handler(sent_msg, process_issue_title_step)


def process_issue_title_step(message):
    title = message.text
    if not title:
        bot.send_message(CHAT_ID, "Invalid title...")
        return
    kb = types.ReplyKeyboardMarkup(
        one_time_keyboard=True, resize_keyboard=True
    )
    kb.add("Skip")
    sent_msg = bot.send_message(
        CHAT_ID,
        "Write the issue text...",
        reply_markup=kb,
        reply_to_message_id=message.message_id,
    )
    bot.register_next_step_handler(sent_msg, process_issue_body_step, title)


def process_issue_body_step(message, title):
    kb = types.ReplyKeyboardMarkup(
        one_time_keyboard=True, resize_keyboard=True
    )
    kb.add("Bug", "Feat", "Check", "Skip")
    sent_msg = bot.send_message(
        CHAT_ID,
        "Choose the issue label...",
        reply_markup=kb,
        reply_to_message_id=message.message_id,
    )
    body = message.text
    if body == "Skip":
        body = ""
    bot.register_next_step_handler(
        sent_msg, process_issue_label_step, title, body
    )


def process_issue_label_step(message, title, body):
    # Remove the reply keyboard
    bot.send_message(
        CHAT_ID,
        "Creating the issue...",
        reply_markup=types.ReplyKeyboardRemove(),
    )
    label = message.text
    label = [] if label == "Skip" else [label]
    issue_url = create_issue_api(title, body, label)
    if issue_url:
        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(types.InlineKeyboardButton(text="Details", url=issue_url))
        bot.send_message(
            CHAT_ID, "The issue created successfully.", reply_markup=kb
        )
    else:
        bot.send_message(CHAT_ID, "The issue is not created.")


@bot.message_handler(commands=["stuboff"])
@check_group_chat
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
@check_group_chat
def send_help_info(message):
    """Sends information about the bot - (description, commands)."""
    bot.send_message(message.chat.id, TEXT_MESSAGES["help"])


bot.infinity_polling()
