"""Settings for the bot."""
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
NOTED_JOB = os.getenv("NOTED_JOB")
STUB_OFF_JOB = os.getenv("STUB_OFF_JOB")
