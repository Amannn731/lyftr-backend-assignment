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


def fetch_messages(
    limit: int,
    offset: int,
    from_msisdn: str | None,
    since: str | None,
    q: str | None,
):
    conn = get_connection()
    cursor = conn.cursor()

    conditions = []
    params = []

    if from_msisdn:
        conditions.append("from_msisdn = ?")
        params.append(from_msisdn)

    if since:
        conditions.append("ts >= ?")
        params.append(since)

    if q:
        conditions.append("LOWER(text) LIKE ?")
        params.append(f"%{q.lower()}%")

    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    total_query = f"SELECT COUNT(*) FROM messages {where_clause}"
    cursor.execute(total_query, params)
    total = cursor.fetchone()[0]

    data_query = f"""
        SELECT message_id, from_msisdn, to_msisdn, ts, text
        FROM messages
        {where_clause}
        ORDER BY ts ASC, message_id ASC
        LIMIT ? OFFSET ?
    """
    cursor.execute(data_query, params + [limit, offset])
    rows = cursor.fetchall()

    conn.close()

    data = [
        {
            "message_id": r[0],
            "from": r[1],
            "to": r[2],
            "ts": r[3],
            "text": r[4],
        }
        for r in rows
    ]

    return data, total
