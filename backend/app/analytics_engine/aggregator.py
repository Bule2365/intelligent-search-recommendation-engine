import sqlite3


def top_search_queries(conn: sqlite3.Connection, limit: int = 10) -> list[dict]:
    rows = conn.execute(
        """
        SELECT search_query, COUNT(*) AS count
        FROM events
        WHERE event_type = 'search_performed' AND search_query IS NOT NULL
        GROUP BY search_query
        ORDER BY count DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    return [dict(r) for r in rows]


def funnel_summary(conn: sqlite3.Connection) -> dict:
    """Hitung jumlah event per tipe -- proxy untuk funnel search -> view ->
    click -> add_to_cart -> purchase yang dibahas di Bagian 6.2.2."""
    rows = conn.execute(
        "SELECT event_type, COUNT(*) AS count FROM events GROUP BY event_type"
    ).fetchall()
    return {r["event_type"]: r["count"] for r in rows}


def click_through_rate(conn: sqlite3.Connection) -> float:
    searches = conn.execute(
        "SELECT COUNT(*) FROM events WHERE event_type = 'search_performed'"
    ).fetchone()[0]
    clicks = conn.execute(
        "SELECT COUNT(*) FROM events WHERE event_type = 'product_click'"
    ).fetchone()[0]
    if searches == 0:
        return 0.0
    return round(clicks / searches, 4)


def category_popularity(conn: sqlite3.Connection, limit: int = 10) -> list[dict]:
    rows = conn.execute(
        """
        SELECT p.category AS category, COUNT(*) AS interactions
        FROM events e
        JOIN products p ON e.product_id = p.product_id
        GROUP BY p.category
        ORDER BY interactions DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    return [dict(r) for r in rows]


def daily_event_counts(conn: sqlite3.Connection, days: int = 14) -> list[dict]:
    rows = conn.execute(
        """
        SELECT substr(timestamp, 1, 10) AS day, COUNT(*) AS count
        FROM events
        GROUP BY day
        ORDER BY day DESC
        LIMIT ?
        """,
        (days,),
    ).fetchall()
    return [dict(r) for r in rows]
