import argparse
import json
import time
from pathlib import Path

from sentence_transformers import SentenceTransformer

import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))
from app.search_engine.semantic_search import build_product_table, MODEL_NAME


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=str, default="../../data/raw")
    parser.add_argument("--db-path", type=str, default="../../data/lancedb")
    parser.add_argument("--batch-size", type=int, default=32)
    args = parser.parse_args()

    print(f"Loading model {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)

    products = json.load(open(Path(args.data_dir) / "products.json", encoding="utf-8"))
    print(f"Encoding {len(products)} products (batch_size={args.batch_size})...")

    t0 = time.time()
    n = build_product_table(
        products, model, db_path=args.db_path, batch_size=args.batch_size
    )
    elapsed = time.time() - t0
    print(f"Done. {n} vectors written to {args.db_path} in {elapsed:.1f}s")


if __name__ == "__main__":
    main()
