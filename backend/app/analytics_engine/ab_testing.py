import hashlib
import sqlite3
from datetime import datetime, timezone


def assign_variant(
    experiment_id: str, user_id: str, split: dict[str, float] | None = None
) -> str:
    """
    split: dict variant -> proporsi (mis. {"control": 0.5, "treatment": 0.5}).
    Default 50/50 dua variant jika tidak diberikan.
    """
    if split is None:
        split = {"control": 0.5, "treatment": 0.5}

    digest = hashlib.md5(f"{experiment_id}:{user_id}".encode()).hexdigest()
    bucket = int(digest, 16) % 100  # 0-99, deterministic untuk pasangan ini

    cumulative = 0.0
    for variant, proportion in split.items():
        cumulative += proportion * 100
        if bucket < cumulative:
            return variant
    return list(split.keys())[-1]  # fallback floating point edge-case


def get_or_assign(
    conn: sqlite3.Connection,
    experiment_id: str,
    user_id: str,
    split: dict[str, float] | None = None,
) -> str:
    row = conn.execute(
        "SELECT variant FROM experiments WHERE experiment_id = ? AND user_id = ?",
        (experiment_id, user_id),
    ).fetchone()
    if row is not None:
        return row["variant"]

    variant = assign_variant(experiment_id, user_id, split)
    conn.execute(
        "INSERT INTO experiments (experiment_id, user_id, variant, assigned_at) VALUES (?, ?, ?, ?)",
        (experiment_id, user_id, variant, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    return variant


def experiment_summary(conn: sqlite3.Connection, experiment_id: str) -> list[dict]:
    """
    Ringkasan distribusi variant -- dipakai untuk sanity-check apakah split
    benar-benar proporsional sebelum menganalisis metrik bisnis (CTR,
    conversion) per variant.
    """
    rows = conn.execute(
        """
        SELECT variant, COUNT(*) AS n_users
        FROM experiments
        WHERE experiment_id = ?
        GROUP BY variant
        """,
        (experiment_id,),
    ).fetchall()
    return [dict(r) for r in rows]
