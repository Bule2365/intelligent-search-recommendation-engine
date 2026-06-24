from datetime import datetime, timezone
import sqlite3


def log_event(
    conn: sqlite3.Connection,
    user_id: str,
    event_type: str,
    product_id: str | None = None,
    search_query: str | None = None,
) -> int:
    """
    Menyimpan event ke tabel events.

    Return:
        event_id (INTEGER PRIMARY KEY)
    """

    timestamp = datetime.now(timezone.utc).isoformat()

    cursor = conn.execute(
        """
        INSERT INTO events (
            user_id,
            event_type,
            product_id,
            search_query,
            timestamp
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            user_id,
            event_type,
            product_id,
            search_query,
            timestamp,
        ),
    )

    conn.commit()

    return cursor.lastrowid
