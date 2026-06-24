import sqlite3
from contextlib import contextmanager

from app.config import SQLITE_PATH


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(SQLITE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # akses kolom by name: row["title"]
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn


@contextmanager
def db_session():
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


def fetch_products_by_ids(
    conn: sqlite3.Connection, product_ids: list[str]
) -> dict[str, dict]:
    """Ambil detail produk lengkap untuk daftar product_id, kembalikan sebagai dict
    {product_id: row_dict} supaya pemanggil bisa mengurutkan ulang sesuai ranking
    dari search/recommendation engine (urutan SQL tidak dijamin sama)."""
    if not product_ids:
        return {}
    placeholders = ",".join("?" * len(product_ids))
    rows = conn.execute(
        f"SELECT * FROM products WHERE product_id IN ({placeholders})", product_ids
    ).fetchall()
    return {row["product_id"]: dict(row) for row in rows}


def fetch_all_products(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute("SELECT * FROM products").fetchall()
    return [dict(r) for r in rows]
