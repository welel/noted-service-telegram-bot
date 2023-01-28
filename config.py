"""This module contains environment variables used in the Noted project.

The module uses the dotenv library to parse a `.env` file and load the
variables inside into environment variables.
"""
import os

from dotenv import load_dotenv


# Parse a `.env` file and load the variables inside into environment variables
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
# TELEGRAM_CHAT_ID (int)
TELEGRAM_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID"))

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = os.getenv("REPO_OWNER")
REPO_NAME = os.getenv("REPO_NAME")

JENKINS_HOST = os.getenv("JENKINS_HOST")
JENKINS_USERNAME = os.getenv("JENKINS_USERNAME")
JENKINS_PASSWORD = os.getenv("JENKINS_PASSWORD")
# A pipline for deploying the website ot the prodaction.
CD_JOB = os.getenv("CD_JOB")
# A pipline with Docker, Django, HTTP, PostgreSQL tests.
CI_JOB = os.getenv("CI_JOB")
BLUE_OCEAN_DASHBOARD_PATH = os.getenv("BLUE_OCEAN_DASHBOARD_PATH")

OPENAI_KEY = os.getenv("OPENAI_KEY")

# Server information for `sinfo` command
SERVER_INFO_1 = os.getenv("SERVER_INFO_1")
SERVER_INFO_2 = os.getenv("SERVER_INFO_2")
SERVER_INFO_3 = os.getenv("SERVER_INFO_3")
SERVER_INFO_4 = os.getenv("SERVER_INFO_4")
SERVER_INFO_5 = os.getenv("SERVER_INFO_5")
SERVER_INFO_6 = os.getenv("SERVER_INFO_6")
