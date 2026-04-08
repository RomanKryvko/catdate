from enum import Enum
from typing import Callable
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from catdate.storage import user_repository, conversation_repository

class MenuState(int, Enum):
    SELECT_CHAT = 1
    SELECT_ACTION = 2


class CallbackKey(str, Enum):
    GO_BACK = 'go_back'
    SCHEDULE = 'schedule'
    ENABLE_REPLY = 'enable_reply'
    POST_NOW = 'post_now'


class Menu:
    def __init__(self, state: MenuState = MenuState.SELECT_CHAT, chat_id: int | None = None):
        self._state = state
        self._chat_id = chat_id

    @property
    def state(self) -> MenuState:
        return self._state

    @state.setter
    def state(self, value: MenuState):
        self._state = value

    @property
    def chat_id(self) -> int | None:
        return self._chat_id

    @chat_id.setter
    def chat_id(self, value: int):
        self._chat_id = value

    def render(self, chat_data: dict | None = None) -> InlineKeyboardMarkup:
        if self._state == MenuState.SELECT_CHAT:
            if not chat_data:
                raise ValueError("Chat data is required to select a chat.")
            keyboard = []
            for id, name in chat_data.items():
                keyboard.append([InlineKeyboardButton(name, callback_data=id)])
            return InlineKeyboardMarkup(keyboard)
        elif self._state == MenuState.SELECT_ACTION:
            keyboard = [[InlineKeyboardButton("Go back", callback_data=CallbackKey.GO_BACK)],
                        [InlineKeyboardButton("Schedule", callback_data=CallbackKey.SCHEDULE)],
                        [InlineKeyboardButton("Enable replies", callback_data=CallbackKey.ENABLE_REPLY)],
                        [InlineKeyboardButton("Post now", callback_data=CallbackKey.POST_NOW)]]
            return InlineKeyboardMarkup(keyboard)
        raise ValueError(f"State {self._state} is not supported.")

    async def menu_entrypoint(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user is None:
            return
        if update.message is None:
            return

        user_id = update.effective_user.id

        conversation_repository.save_menu_state(update.effective_chat.id, self.state, self.chat_id)
        chat_data = await fetch_chat_data(user_id, context)
        if chat_data:
            await update.message.reply_text("Choose a chat:", reply_markup=self.render(chat_data))
        else:
            await update.message.reply_text("You are not an administrator in any known chats.")

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        if query is None:
            return

        await query.answer()
        data = query.data
        if data is None:
            return

        if self.state == MenuState.SELECT_CHAT:
            self.chat_id = int(data)
            self.state = MenuState.SELECT_ACTION
            conversation_repository.save_menu_state(update.effective_chat.id, self.state, self.chat_id)
            await query.edit_message_text("Pick an option", reply_markup=self.render())
        elif self.state == MenuState.SELECT_ACTION:
            await self._callbacks[data](self, update, context)

        context.drop_callback_data(query)

    async def handle_go_back(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        if query is None:
            return
        if update.effective_user is None:
            return

        self.state = MenuState.SELECT_CHAT
        conversation_repository.save_menu_state(update.effective_chat.id, self.state, self.chat_id)
        chat_data = await fetch_chat_data(update.effective_user.id, context)
        if chat_data:
            await query.edit_message_text("Choose a chat:", reply_markup=self.render(chat_data))
        else:
            await query.edit_message_text("You are not an administrator in any known chats.")

    async def handle_schedule(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        if query is None:
            return
        await query.edit_message_text("You picked SCHEDULE")

    async def handle_toggle_reply(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        if query is None:
            return
        await query.edit_message_text("You picked ENABLE_REPLY")

    async def handle_post_now(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        if query is None:
            return
        await query.edit_message_text("You picked POST_NOW")

    _callbacks: dict[str, Callable[[Menu, Update, ContextTypes.DEFAULT_TYPE]]] = {
        CallbackKey.GO_BACK: handle_go_back,
        CallbackKey.SCHEDULE: handle_schedule,
        CallbackKey.ENABLE_REPLY: handle_toggle_reply,
        CallbackKey.POST_NOW: handle_post_now,
    }


async def fetch_chat_data(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> dict:
    chat_data = dict()
    try:
        for chat in user_repository.get_chats_by_user(user_id):
            chat_info = await context.bot.get_chat(chat)
            chat_data[chat] = chat_info.title
    except KeyError:
        pass
    return chat_data

