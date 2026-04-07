from catdate.storage import db

def add_user_chat(user_id: int, chat_id: int):
    con = db.connect()
    cursor = con.cursor()
    data = ({"user_id": user_id, "chat_id": chat_id})
    cursor.execute("INSERT INTO user_chat VALUES(:user_id, :chat_id)", data)
    con.commit()

def remove_user_chat(user_id: int, chat_id: int):
    con = db.connect()
    cursor = con.cursor()
    data = ({"user_id": user_id, "chat_id": chat_id})
    cursor.execute("DELETE FROM user_chat WHERE user_id = :user_id AND chat_id = :chat_id", data)

def get_chats_by_user(user_id: int) -> list[int]:
    con = db.connect()
    cursor = con.cursor()
    data = ({"user_id": user_id})
    result = cursor.execute("SELECT chat_id FROM user_chat WHERE user_id = :user_id", data)
    return [row[0] for row in result]
