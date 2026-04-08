from catdate.storage import db

def get_menu_state(chat_id: int) -> tuple[int, int] | None:
    cursor = db.connect().cursor()
    cursor.execute("SELECT menu_state, menu_chat_id FROM conversation WHERE chat_id = :chat_id", {"chat_id": chat_id})
    #NOTE: we expect exactly 1 or 0 rows
    for row in cursor:
        return (row[0], row[1])
    return None

def save_menu_state(chat_id: int, menu_state: int, menu_chat_id: int | None):
    conn = db.connect()
    cursor = conn.cursor()

    data = {'chat_id': chat_id, 'menu_state': menu_state, 'menu_chat_id': menu_chat_id}
    cursor.execute("""INSERT INTO conversation (chat_id, menu_state, menu_chat_id)
        VALUES (:chat_id, :menu_state, :menu_chat_id)
        ON CONFLICT(chat_id) DO UPDATE SET
            menu_state = excluded.menu_state,
            menu_chat_id = excluded.menu_chat_id
        """, data)

    conn.commit()
