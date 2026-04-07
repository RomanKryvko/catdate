from enum import Enum
import logging
from telegram import Chat, ChatMemberUpdated, InlineKeyboardButton, InlineKeyboardMarkup, Update, ChatMember
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, ChatMemberHandler, ContextTypes, CommandHandler
from catdate.image.image import put_text_over_image

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
# higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

async def start (update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="hello world")


async def image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=put_text_over_image())


def extract_status_change(chat_member_update: ChatMemberUpdated) -> tuple[bool, bool] | None:
    """Takes a ChatMemberUpdated instance and extracts whether the 'old_chat_member' was a member
    of the chat and whether the 'new_chat_member' is a member of the chat. Returns None, if
    the status didn't change.
    """
    status_change = chat_member_update.difference().get("status")
    old_is_member, new_is_member = chat_member_update.difference().get("is_member", (None, None))

    if status_change is None:
        return None

    old_status, new_status = status_change
    was_member = old_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (old_status == ChatMember.RESTRICTED and old_is_member is True)
    is_member = new_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (new_status == ChatMember.RESTRICTED and new_is_member is True)

    return was_member, is_member


async def track_chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #TODO: track member status
    result = extract_status_change(update.my_chat_member)
    if result is None:
        return

    was_member, is_member = result
    chat = update.effective_chat
    cause = update.effective_user.id
    if chat.type == Chat.CHANNEL:
        if is_member and not was_member:
            context.bot_data.setdefault("users", {}).setdefault(cause, set()).add(chat.id)
        elif was_member and not is_member:
            context.bot_data.setdefault("users", {}).setdefault(cause, set()).discard(chat.id)


class MenuState(int, Enum):
    SELECT_CHAT = 1
    SELECT_ACTION = 2


class CallbackKey(str, Enum):
    GO_BACK = 'go_back'
    SCHEDULE = 'schedule'
    ENABLE_REPLY = 'enable_reply'
    POST_NOW = 'post_now'


class Menu:
    def __init__(self):
        self._state = MenuState.SELECT_CHAT
        self._chat_id = None

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

    def render(self, chat_data: dict = dict()) -> InlineKeyboardMarkup:
        if self._state == MenuState.SELECT_CHAT:
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


inline_menu = Menu()

async def fetch_chat_data(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> dict:
    chat_data = dict()
    try:
        for chat in context.bot_data["users"][user_id]:
            chat_info = await context.bot.get_chat(chat)
            chat_data[chat] = chat_info.title
    except KeyError:
        pass
    return chat_data


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    chat_data = await fetch_chat_data(user_id, context)
    if not chat_data:
        await update.message.reply_text("You are not an administrator in any known chats.")
        return

    await update.message.reply_text("Choose a chat:", reply_markup=inline_menu.render(chat_data))


async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query is None:
        return

    await query.answer()
    data = query.data
    if data is None:
        return

    if inline_menu.state == MenuState.SELECT_CHAT:
        inline_menu.chat_id = int(data)
        inline_menu.state = MenuState.SELECT_ACTION
        markup = inline_menu.render()
        await query.edit_message_text("Pick an option", reply_markup=markup)
    elif inline_menu.state == MenuState.SELECT_ACTION:
        if data == CallbackKey.GO_BACK:
            inline_menu.state = MenuState.SELECT_CHAT
            user_id = update.effective_user.id
            chat_data = await fetch_chat_data(user_id, context)
            if not chat_data:
                await query.edit_message_text("You are not an administrator in any known chats.")
                return
            await query.edit_message_text("Choose a chat:", reply_markup=inline_menu.render(chat_data))
        elif data == CallbackKey.SCHEDULE:
            await query.edit_message_text("You picked SCHEDULE")
        elif data == CallbackKey.ENABLE_REPLY:
            await query.edit_message_text("You picked ENABLE_REPLY")
        elif data == CallbackKey.POST_NOW:
            await query.edit_message_text("You picked POST_NOW")

    context.drop_callback_data(query)


def run_bot(token: str):
    application = ApplicationBuilder().token(token).build()
    handlers = [
        CommandHandler('start', start),
        CommandHandler('img', image),
        CommandHandler('menu', menu),
        CallbackQueryHandler(handle),
        ChatMemberHandler(track_chats),
    ]
    for h in handlers:
        application.add_handler(h)

    application.run_polling()

