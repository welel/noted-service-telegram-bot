#!/usr/bin/env python3.8
"""This module contains a telegram bot for the NoteD developer team.

The bot provides services to help the team manage developing processes
and get developing information. It provides requests to GitHub and Jenkins.

The bot can help with: 
1. List last commits, build them to the prodaction, test them before the prodaction. 
2. Create issues to the project.
3. Inspect server info.
4. Inspect Jenkins jobs info.
5. Ping a website
6. And just talk heart to heart (OpenAI chatbot). 

Commands: 
/commit - Display last commit
/commits - Display N commits
/issue - Create an issue 
/ping - Ping the website
/sinfo - Info about the server
/jinfo - Info about Jenkins jobs
/c - [/chat] Speak with AI 
/help - Bot information  

The bot uses:
    `telebot` library for creating a Telegram Bot,
    `requests` library for requests to GitHub API,
    `api4jenkins` library for requests to Jenkins API,
    `openai` library for AI chatbot.  

"""
import functools
import os
import requests

import telebot
from telebot import types
from telebot.util import extract_arguments

from aichat import get_answer
from config import (
    TELEGRAM_TOKEN,
    TELEGRAM_CHAT_ID as CHAT_ID,
    CI_JOB,
    CD_JOB,
    BLUE_OCEAN_DASHBOARD_PATH,
    JENKINS_HOST,
    SERVER_INFO_1,
    SERVER_INFO_2,
    SERVER_INFO_3,
    SERVER_INFO_4,
    SERVER_INFO_5,
    SERVER_INFO_6,
)
from formatters import format_commit
from github import get_commits, create_issue as create_issue_api
from jenkins import build_job, get_job_details
from callback import form_callback_query, get_data


TEXT_MESSAGES = {
    "welcome": str(
        "Welcome to the NoteD Service Bot!\n\n"
        "The telegram bot provides the NoteD developer team with services "
        + "to help them manage developing processes and get developing "
        + "information. Provides requests to GitHub and Jenkins."
    ),
    "help": str(
        "I am a service bot for the NoteD team.\n\n"
        "I can help with:\n"
        "CI\CD management: list commits for buttons; and with following by the command list.\n\n"
        "Commands:\n"
        "/commit - Display last commit\n"
        "/commits - Display N commits\n"
        "/issue - Create an issue\n"
        "/ping - Ping the website\n"
        "/sinfo - Info about the server\n"
        "/jinfo - Info about Jenkins jobs\n"
        "/c - [/chat] Speak to AI\n"
        "/help - Bot information"
    ),
    "wrong_chat": str(
        "Hi there!\n"
        "Thanks for trying me out. However, this bot can only be "
        + "used in the NoteD developer group chat.\n\n"
        "Check out our profect!\n"
        "https://welel-noted.site/"
    ),
    "server_info": str(
        "<b>Docker env infra path:</b>\n"
        "<code>{}</code>\n\n"
        "<b>Docker env noted path:</b>\n"
        "<code>{}</code>\n\n"
        "<b>Connect to DB system user:</b>\n"
        "<code>{}</code>\n"
        "<code>{}</code>\n\n"
        "<b>Connect to DB noted user:</b>\n"
        "<code>{}</code>\n"
        "<code>{}</code>".format(
            SERVER_INFO_1,
            SERVER_INFO_2,
            SERVER_INFO_3,
            SERVER_INFO_4,
            SERVER_INFO_5,
            SERVER_INFO_6,
        )
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


@bot.message_handler(commands=["ping"])
@check_group_chat
def ping_website(message):
    """Checks the status code of the NoteD website."""
    res = requests.get("https://welel-noted.site", timeout=7)
    bot.send_message(message.chat.id, "Status code: " + str(res.status_code))


@bot.message_handler(commands=["commit"])
@check_group_chat
def display_commits(message):
    """Display last commit with inline buttons for info and managment."""
    display_commits_handler(message, number=1)


@bot.message_handler(commands=["commits"])
@check_group_chat
def display_commits(message):
    """Display last N commits with inline buttons for info and managment.

    Telegram usage:
        /commits 10
    """
    num_commits = extract_arguments(message.text)
    if not num_commits:
        bot.send_message(message.chat.id, "Usage - /commits [number commits].")
        return

    try:
        num_commits = int(num_commits)
    except ValueError:
        bot.send_message(message.chat.id, "Invalid value.")
        return

    display_commits_handler(message, number=num_commits)


def display_commits_handler(message, number: int = 1):
    """Sends last commits with inline buttons.

    Displays commit information - comment, hash.
    Buttons:
        1. Starts a Jenkins job to build this commit in the prodaction.
        2. Starts a Jenkins job to test the project.
        3. Url to the GitHub commit.

    Args:
        number: a number of commits.
    """
    try:
        commits = get_commits(num=number)
    except Exception as error:
        bot.send_message(message.chat.id, "An error has occurred, try later.")
        print(error)
    for i, commit in enumerate(commits):
        commit_msg = format_commit(commit, nn=i + 1)
        kb = types.InlineKeyboardMarkup(row_width=2)
        data_build = form_callback_query("build_commit", commit["sha"])
        data_test = form_callback_query("build_test", commit["sha"])
        kb.add(
            types.InlineKeyboardButton(text="Build", callback_data=data_build),
            types.InlineKeyboardButton(text="Test", callback_data=data_test),
            types.InlineKeyboardButton(text="Details", url=commit["url"]),
        )
        bot.send_message(
            CHAT_ID, commit_msg, parse_mode="HTML", reply_markup=kb
        )


@bot.callback_query_handler(func=lambda cb: cb.data.startswith("build_commit"))
def build_commit_handler(callback):
    """Handles the `Build` button of a commit, starts the Jenkins job.

    If a `Build` button was pressed starts the Jenkins job that builds
    the provided commit to the prodaction.
    """
    commit_hash = get_data(callback.data)
    msg = build_job(CD_JOB, COMMIT_HASH=commit_hash)
    msg = f"Build for {commit_hash} has requested." if msg == "build" else msg
    kb = types.InlineKeyboardMarkup(row_width=1)
    blue_ocean_url = JENKINS_HOST + BLUE_OCEAN_DASHBOARD_PATH
    kb.add(types.InlineKeyboardButton(text="Blue Ocean", url=blue_ocean_url))
    bot.send_message(CHAT_ID, msg, reply_markup=kb)


@bot.callback_query_handler(func=lambda cb: cb.data.startswith("build_test"))
def build_test_handler(callback):
    """Handles the `Test` button of a commtt, starts the Jenkins job.

    If a `Test` button was pressed starts the Jenkins job that tests
    the provided commit for the prodaction.
    """
    commit_hash = get_data(callback.data)
    msg = build_job(CI_JOB, COMMIT_HASH=commit_hash)
    msg = f"Tests for {commit_hash} has requested." if msg == "build" else msg
    kb = types.InlineKeyboardMarkup(row_width=1)
    blue_ocean_url = JENKINS_HOST + BLUE_OCEAN_DASHBOARD_PATH
    kb.add(types.InlineKeyboardButton(text="Blue Ocean", url=blue_ocean_url))
    bot.send_message(CHAT_ID, msg, reply_markup=kb)


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
    kb.add("bug", "feat", "docs", "refactor", "devops", "check", "Skip")
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


# c: 1 - in EN, 2 - in RU [short from chat]
@bot.message_handler(commands=["c", "??", "chat"])
@check_group_chat
def chatbot(message):
    """API request to the OpenAI chatbot.

    Telegram usage:
        /chat [message]
    """
    text = extract_arguments(message.text)
    ai_answer = get_answer(text)
    bot.send_message(message.chat.id, ai_answer)


@bot.message_handler(commands=["sinfo"])
@check_group_chat
def send_server_info(message):
    """Sends information about server data and infrastructure."""
    image = open("imgs/infra.jpeg", "rb")
    bot.send_photo(message.chat.id, image)
    bot.send_message(
        message.chat.id, TEXT_MESSAGES["server_info"], parse_mode="HTML"
    )


@bot.message_handler(commands=["jinfo"])
@check_group_chat
def send_jenkins_jobs_info(message):
    """Sends information about jenkins jobs."""
    jobs_info = get_job_details()
    bot.send_message(message.chat.id, jobs_info)


@bot.message_handler(commands=["help"])
@check_group_chat
def send_help_info(message):
    """Sends information about the bot - (description, commands)."""
    bot.send_message(message.chat.id, TEXT_MESSAGES["help"])


if __name__ == "__main__":
    bot.infinity_polling()
