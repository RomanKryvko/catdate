import sqlite3

_conn: sqlite3.Connection | None = None

def init():
    query = """CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY);
CREATE TABLE IF NOT EXISTS chat (id INTEGER PRIMARY KEY, type TEXT);
CREATE TABLE IF NOT EXISTS conversation (chat_id INTEGER PRIMARY KEY, menu_state INTEGER, menu_chat_id INTEGER);
CREATE TABLE IF NOT EXISTS user_chat (user_id INTEGER NOT NULL, chat_id INTEGER NOT NULL, PRIMARY KEY (user_id, chat_id));"""

    cursor = connect().cursor()
    cursor.executescript(query)


def connect() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        _conn = sqlite3.connect("bot.db", check_same_thread=False)
    return _conn
