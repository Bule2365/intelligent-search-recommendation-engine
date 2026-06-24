import argparse
import json
import sqlite3
from pathlib import Path

SCHEMA = """
PRAGMA journal_mode = WAL;  -- read & write tidak saling memblokir (Bagian 3.7)
 
CREATE TABLE IF NOT EXISTS products (
    product_id   TEXT PRIMARY KEY,
    title        TEXT NOT NULL,
    description  TEXT NOT NULL,
    category     TEXT NOT NULL,
    brand        TEXT NOT NULL,
    price        INTEGER NOT NULL,
    stock        INTEGER NOT NULL,
    rating       REAL NOT NULL,
    num_reviews  INTEGER NOT NULL,
    created_at   TEXT NOT NULL
);
 
CREATE TABLE IF NOT EXISTS users (
    user_id      TEXT PRIMARY KEY,
    name         TEXT NOT NULL,
    email        TEXT NOT NULL,
    signup_date  TEXT NOT NULL
);
 
CREATE TABLE IF NOT EXISTS events (
    event_id     INTEGER PRIMARY KEY,
    user_id      TEXT NOT NULL,
    event_type   TEXT NOT NULL,
    product_id   TEXT,
    search_query TEXT,
    timestamp    TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (user_id),
    FOREIGN KEY (product_id) REFERENCES products (product_id)
);
 
CREATE TABLE IF NOT EXISTS orders (
    order_id     INTEGER PRIMARY KEY,
    user_id      TEXT NOT NULL,
    product_id   TEXT NOT NULL,
    quantity     INTEGER NOT NULL,
    total_price  INTEGER NOT NULL,
    order_date   TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (user_id),
    FOREIGN KEY (product_id) REFERENCES products (product_id)
);
 
CREATE TABLE IF NOT EXISTS experiments (
    experiment_id   TEXT NOT NULL,
    user_id         TEXT NOT NULL,
    variant         TEXT NOT NULL,
    assigned_at     TEXT NOT NULL,
    PRIMARY KEY (experiment_id, user_id)
);
 
-- Index untuk query yang sering dipakai (Bagian 3.7)
CREATE INDEX IF NOT EXISTS idx_products_category ON products (category);
CREATE INDEX IF NOT EXISTS idx_events_user ON events (user_id);
CREATE INDEX IF NOT EXISTS idx_events_product ON events (product_id);
CREATE INDEX IF NOT EXISTS idx_events_type ON events (event_type);
CREATE INDEX IF NOT EXISTS idx_orders_user ON orders (user_id);
CREATE INDEX IF NOT EXISTS idx_orders_product ON orders (product_id);
"""


def load_json(path: Path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=str, default="../../data/raw")
    parser.add_argument("--db-path", type=str, default="../../data/ecommerce.db")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    db_path = Path(args.db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA)

    products = load_json(data_dir / "products.json")
    users = load_json(data_dir / "users.json")
    events = load_json(data_dir / "events.json")
    orders = load_json(data_dir / "orders.json")

    conn.executemany(
        "INSERT OR REPLACE INTO products VALUES (?,?,?,?,?,?,?,?,?,?)",
        [
            (
                p["product_id"],
                p["title"],
                p["description"],
                p["category"],
                p["brand"],
                p["price"],
                p["stock"],
                p["rating"],
                p["num_reviews"],
                p["created_at"],
            )
            for p in products
        ],
    )
    conn.executemany(
        "INSERT OR REPLACE INTO users VALUES (?,?,?,?)",
        [(u["user_id"], u["name"], u["email"], u["signup_date"]) for u in users],
    )
    conn.executemany(
        "INSERT OR REPLACE INTO events VALUES (?,?,?,?,?,?)",
        [
            (
                e["event_id"],
                e["user_id"],
                e["event_type"],
                e["product_id"],
                e["search_query"],
                e["timestamp"],
            )
            for e in events
        ],
    )
    conn.executemany(
        "INSERT OR REPLACE INTO orders VALUES (?,?,?,?,?,?)",
        [
            (
                o["order_id"],
                o["user_id"],
                o["product_id"],
                o["quantity"],
                o["total_price"],
                o["order_date"],
            )
            for o in orders
        ],
    )

    conn.commit()
    counts = {
        t: conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        for t in ["products", "users", "events", "orders"]
    }
    conn.close()
    print(f"Seeded SQLite at {db_path}: {counts}")


if __name__ == "__main__":
    main()
