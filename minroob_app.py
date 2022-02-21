from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message, InlineKeyboardButton

from time import sleep
from threading import Timer
import emoji
from typing import List
from game import Board, Cell


class MinroobApp:
    BOT_USERNAME = "@minroobot"
    PLAY_IN_MINROOB_LEAGUE_MESSAGE = {"en": "🏆 Play in Minroob League", "fa": "🏆 بازی در لیگ مینروب"}

    def __init__(self, api_id: str, api_hash: str, sleep_time: int = 0, allow_start_again_in_bot_chat: bool = False):
        self.client = Client("minroob-app", api_id, api_hash)
        self.set_handlers()

        self.sleep_time = sleep_time
        self.allow_start_again_in_bot_chat = allow_start_again_in_bot_chat
        self.client_name: str = None
        self.wait_for_opponent: Timer = None

    def run(self):
        self.client.run()

    def set_handlers(self):
        self.client.add_handler(MessageHandler(self.bot_chat,
                                               filters.chat(MinroobApp.BOT_USERNAME) &
                                               filters.inline_keyboard))

        self.client.add_handler(MessageHandler(self.inline,
                                               ~filters.chat(MinroobApp.BOT_USERNAME) &
                                               filters.via_bot &
                                               filters.inline_keyboard &
                                               filters.create(lambda _, __, message: f"@{message.via_bot.username}" == MinroobApp.BOT_USERNAME)))

        self.client.add_handler(MessageHandler(self.me_chat,
                                               filters.chat("me") &
                                               filters.text &
                                               ~filters.edited))

    def extract_board(self, inline_keyboard: List[List[InlineKeyboardButton]]) -> List[List[int]]:
        board = [[Cell.EMOJI_UNICODE_SWITCH[emoji.demojize(cell.text.strip("️"))]
                  for cell in row]
                 for row in inline_keyboard[:Board.SIZES[0]]]
        return board

    def play(self, client: Client, message: Message):
        inline_keyboard = message.reply_markup.inline_keyboard
        extracted_board = self.extract_board(inline_keyboard)
        board = Board(extracted_board)

        selected_cell = board.choose()
        selected_cell_coordinate = selected_cell.coordinate
        selected_cell_callback_data = inline_keyboard[selected_cell_coordinate.x][selected_cell_coordinate.y].callback_data

        sleep(self.sleep_time)
        client.request_callback_answer(message.chat.id, message.message_id, selected_cell_callback_data)

    def fuck(self, client: Client, message: Message, in_bot_chat: bool = False):
        text = message.text
        text_lines = text.splitlines()
        player_name = text_lines[0].split(": ", 1)[1].rsplit(" ", 1)[0]

        if self.client_name is None:
            self.client_name = client.get_me().first_name

        if player_name == self.client_name:
            self.play(client, message)

        elif in_bot_chat:
            round_time = int(text_lines[3].split(": ", 1)[1].rsplit(" ", 1)[0])
            self.wait_for_opponent = Timer(round_time + 1, self.play, args=[client, message])
            self.wait_for_opponent.start()

    def bot_chat(self, client: Client, message: Message):
        inline_keyboard = message.reply_markup.inline_keyboard
        first_button_callback_data = inline_keyboard[0][0].callback_data

        if first_button_callback_data is None:
            if emoji.demojize(message.text.splitlines()[0]).startswith(
                    ":trophy:") and self.allow_start_again_in_bot_chat:
                client.request_callback_answer(message.chat.id, message.message_id, inline_keyboard[-2][0].callback_data)
                if self.wait_for_opponent is not None:
                    self.wait_for_opponent.cancel()

        elif first_button_callback_data == "room:commands.new_random_game:0":
            client.request_callback_answer(message.chat.id,
                                           message.message_id,
                                           first_button_callback_data)

        elif first_button_callback_data == "league:cancel_wait:0":
            pass

        elif first_button_callback_data.endswith(":puzzle:1"):
            language = first_button_callback_data.split(":", 1)[0]
            client.send_message(MinroobApp.BOT_USERNAME, MinroobApp.PLAY_IN_MINROOB_LEAGUE_MESSAGE[language])

        elif first_button_callback_data.startswith("mine:1:"):
            try:
                if self.wait_for_opponent is not None:
                    self.wait_for_opponent.cancel()
                self.fuck(client, message, in_bot_chat=True)
            except TimeoutError:
                pass

    def me_chat(self, client: Client, message: Message):
        text = message.text
        second_part = text.split("-", 1)[1].lower()

        if text == "play-minroob":
            client.send_message(MinroobApp.BOT_USERNAME, "/start")

        elif text.startswith("sleep-") and second_part.isnumeric():
            self.sleep_time = int(second_part)

        elif text.startswith("allow-") and second_part in ["true", "false"]:
            self.allow_start_again_in_bot_chat = True if second_part == "true" else False

    def inline(self, client: Client, message: Message):
        inline_keyboard = message.reply_markup.inline_keyboard
        first_button_callback_data = inline_keyboard[0][0].callback_data

        if first_button_callback_data is None:
            pass

        elif first_button_callback_data.startswith("mine:accept:inline"):
            if not message.from_user.is_self:
                client.request_callback_answer(message.chat.id, message.message_id, first_button_callback_data)

        elif first_button_callback_data.startswith("mine:1:"):
            try:
                self.fuck(client, message)
            except TimeoutError:
                pass
