# NoteD Service Telegram Bot

This telegram bot provides the [NoteD](https://github.com/welel/noted) developer team with services to help them manage developing processes and get developing information. It provides requests to GitHub, Jenkins and OpenAI, and can be used for a variety of tasks.

Check out our website: https://welel-noted.site

## Features 

The NoteD Service Telegram Bot provides the following features: 
- List last commits, build them to the prodaction, test them before the prodaction. 
- Create issues to the project. 
- Set off the stub of the website.
- Ping the website.
- Chatbot for heart to heart conversations (OpenAI). 

## Commands 

The bot has several commands that can be used to access its features: 
- `/commit` - Display last commit 
- `/commits` - Display last 3 commits 
- `/issue` - Create an issue 
- `/stuboff` - Set the stub off 
- `/ping` - Ping the website 
- `/c` - [chat] Speak with AI  
- `/help` - Bot information  

 ## Requirements  

 The NoteD Service Telegram Bot uses several packages:  

 - `telebot` package for creating a Telegram Bot,  
 - `requests` package for requests to GitHub API,  
 - `api4jenkins` package for requests to Jenkins API,  
 - `openai` package for AI chatbot.
 