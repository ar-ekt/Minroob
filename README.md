# Minroob
- An auto play program for [@minroobot](https://telegram.me/minroobot "@minroobot") Telegram bot games with connecting to your Telegram account.
- Used [pyrogram](https://github.com/pyrogram/pyrogram "pyrogram") framework for the part of interacting with Telegram.

## How to Run
1. Replace `api_id` and `api_hash` of your Telegram account in [config.ini](config.ini). (You can obtain an API id for your Telegram account from [here](https://core.telegram.org/api/obtaining_api_id))
2. Install the required libraries mentioned in the [requirements.txt](requirements.txt).
3. Run [main.py](main.py).

## How to Use
Interact with program by sending message in Saved Messages chat.
- You can start a game automatically in the chatbot by sending `play-minroob`.
- You can specify with `allow-true` and `allow-false`, that after the end of a game in the chatbot, another game starts or not. By default, it is specified that a new game will not start.
- You can change the response delay time with `sleep-{time in second}`. The default value is 0.
- Also inline-games are supported.
