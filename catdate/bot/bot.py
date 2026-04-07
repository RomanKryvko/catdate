import logging
from telegram import Chat, ChatMemberUpdated, InlineKeyboardButton, InlineKeyboardMarkup, Update, ChatMember
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, ChatMemberHandler, ContextTypes, CommandHandler
from catdate.image.image import put_text_over_image

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

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


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    chat_data = dict()
    try:
        for chat in context.bot_data["users"][user_id]:
            chat_info = await context.bot.get_chat(chat)
            chat_data[chat] = chat_info.title
    except KeyError:
        await update.message.reply_text("You are not an administrator in any known chats.")
        return

    await update.message.reply_text("Choose a chat:", reply_markup=main_menu_keyboard(chat_data))


def main_menu_keyboard(chats: dict) -> InlineKeyboardMarkup:
    keyboard = []
    for id, name in chats.items():
        keyboard.append([InlineKeyboardButton(name, callback_data=id)])
    return InlineKeyboardMarkup(keyboard)


async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text=f"You picked {query.data}")
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

