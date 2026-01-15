import sqlite3
from datetime import datetime
from app.models import get_connection


def insert_message(message: dict) -> bool:
    """
    Inserts a message into DB.
    Returns True if inserted, False if duplicate.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO messages (
                message_id,
                from_msisdn,
                to_msisdn,
                ts,
                text,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                message["message_id"],
                message["from"],
                message["to"],
                message["ts"],
                message.get("text"),
                datetime.utcnow().isoformat() + "Z",
            ),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Duplicate message_id
        return False
    finally:
        conn.close()
