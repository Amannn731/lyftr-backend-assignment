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

    cursor.execute(f"SELECT COUNT(*) FROM messages {where_clause}", params)
    total = cursor.fetchone()[0]

    cursor.execute(
        f"""
        SELECT message_id, from_msisdn, to_msisdn, ts, text
        FROM messages
        {where_clause}
        ORDER BY ts ASC, message_id ASC
        LIMIT ? OFFSET ?
        """,
        params + [limit, offset],
    )
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


def fetch_stats():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM messages")
    total_messages = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT from_msisdn) FROM messages")
    senders_count = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT from_msisdn, COUNT(*) as cnt
        FROM messages
        GROUP BY from_msisdn
        ORDER BY cnt DESC
        LIMIT 10
        """
    )
    messages_per_sender = [
        {"from": row[0], "count": row[1]}
        for row in cursor.fetchall()
    ]

    cursor.execute("SELECT MIN(ts), MAX(ts) FROM messages")
    row = cursor.fetchone()
    first_message_ts = row[0]
    last_message_ts = row[1]

    conn.close()

    return {
        "total_messages": total_messages,
        "senders_count": senders_count,
        "messages_per_sender": messages_per_sender,
        "first_message_ts": first_message_ts,
        "last_message_ts": last_message_ts,
    }
