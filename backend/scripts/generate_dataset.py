import argparse
import json
import random
import sqlite3
from pathlib import Path

from faker import Faker

fake = Faker("id_ID")

# ---------------------------------------------------------------------------
# 1. TAKSONOMI KATEGORI & TEMPLATE PRODUK
# ---------------------------------------------------------------------------
# Setiap kategori punya kosa kata khasnya sendiri. Ini penting supaya nanti
# semantic search punya sesuatu yang bisa "dipahami maknanya" -- bukan cuma
# kata kunci acak.

CATEGORIES = {
    "Sepatu": {
        "adjectives": [
            "ringan",
            "nyaman",
            "tahan lama",
            "anti slip",
            "breathable",
            "trendy",
        ],
        "nouns": [
            "sepatu lari",
            "sepatu sneakers",
            "sepatu sandal",
            "sepatu formal",
            "sepatu olahraga",
        ],
        "brands": ["Nexa", "Stridon", "Volcra", "Pacefit", "Urbanstep"],
    },
    "Elektronik": {
        "adjectives": [
            "hemat daya",
            "performa tinggi",
            "kompak",
            "tahan banting",
            "fast charging",
        ],
        "nouns": [
            "smartphone",
            "laptop",
            "earphone wireless",
            "power bank",
            "smartwatch",
        ],
        "brands": ["Zentra", "Korelux", "Vexor", "Primtek", "Nuvotech"],
    },
    "Fashion Pria": {
        "adjectives": [
            "slim fit",
            "lengan panjang",
            "bahan katun",
            "anti kusut",
            "casual",
        ],
        "nouns": [
            "kemeja",
            "kaos polo",
            "celana chino",
            "jaket bomber",
            "kemeja flanel",
        ],
        "brands": ["Urbano", "Kelvara", "Maskuline", "Tredline", "Garmen"],
    },
    "Fashion Wanita": {
        "adjectives": [
            "elegan",
            "longgar",
            "bahan adem",
            "motif bunga",
            "korean style",
        ],
        "nouns": ["dress", "blouse", "rok midi", "atasan crop", "cardigan"],
        "brands": ["Bellora", "Sienna", "Lunara", "Mireia", "Velloura"],
    },
    "Peralatan Dapur": {
        "adjectives": [
            "anti lengket",
            "stainless steel",
            "hemat listrik",
            "mudah dibersihkan",
            "kapasitas besar",
        ],
        "nouns": ["panci set", "rice cooker", "blender", "air fryer", "pisau dapur"],
        "brands": ["Domesta", "Koolwell", "Chefina", "Hommie", "Daparoo"],
    },
    "Perawatan Tubuh": {
        "adjectives": [
            "alami",
            "bebas paraben",
            "untuk kulit sensitif",
            "wangi tahan lama",
            "moisturizing",
        ],
        "nouns": ["sabun mandi", "sunscreen", "serum wajah", "shampo", "lotion"],
        "brands": ["Glowra", "Naturee", "Skinique", "Velvae", "Purelis"],
    },
    "Peralatan Olahraga": {
        "adjectives": [
            "portable",
            "anti slip",
            "tahan lama",
            "ringan dibawa",
            "multifungsi",
        ],
        "nouns": [
            "matras yoga",
            "dumbbell",
            "resistance band",
            "sepeda lipat",
            "raket badminton",
        ],
        "brands": ["Flexura", "Ironcore", "Activo", "Sportif", "Enduro"],
    },
    "Aksesoris": {
        "adjectives": [
            "minimalis",
            "tahan air",
            "bahan kulit asli",
            "anti karat",
            "edisi terbatas",
        ],
        "nouns": ["tas selempang", "dompet pria", "jam tangan", "kacamata", "topi"],
        "brands": ["Klassio", "Ferano", "Urbankit", "Lumora", "Stratta"],
    },
}

# ---------------------------------------------------------------------------
# 2. GENERATOR PRODUK
# ---------------------------------------------------------------------------


def generate_products(n_products: int, rng: random.Random) -> list[dict]:
    products = []
    cat_names = list(CATEGORIES.keys())
    for i in range(n_products):
        cat = rng.choice(cat_names)
        spec = CATEGORIES[cat]
        brand = rng.choice(spec["brands"])
        noun = rng.choice(spec["nouns"])
        adj1, adj2 = rng.sample(spec["adjectives"], 2)

        title = f"{brand} {noun.title()} {adj1.title()}"
        description = (
            f"{noun.capitalize()} dari {brand}, dirancang {adj1} dan {adj2}. "
            f"Cocok untuk kebutuhan sehari-hari kategori {cat.lower()}. "
            f"{fake.sentence(nb_words=10)}"
        )

        price = rng.choice(
            [
                rng.randint(15, 99) * 1000,  # produk murah
                rng.randint(100, 499) * 1000,  # produk menengah
                rng.randint(500, 5000) * 1000,  # produk mahal
            ]
        )

        products.append(
            {
                "product_id": f"P{i:06d}",
                "title": title,
                "description": description,
                "category": cat,
                "brand": brand,
                "price": price,
                "stock": rng.randint(0, 500),
                "rating": round(rng.uniform(3.0, 5.0), 1),
                "num_reviews": rng.randint(0, 2000),
                "created_at": fake.date_between(
                    start_date="-2y", end_date="today"
                ).isoformat(),
            }
        )
    return products


# ---------------------------------------------------------------------------
# 3. GENERATOR USER (dengan preferensi kategori tersembunyi)
# ---------------------------------------------------------------------------
# Setiap user diberi 1-3 kategori favorit. Preferensi ini TIDAK disimpan
# eksplisit sebagai kolom -- ia hanya memengaruhi pola order & event yang
# dihasilkan. Recommendation engine harus MENEMUKAN pola ini dari perilaku,
# persis seperti di dunia nyata.


def generate_users(n_users: int, rng: random.Random) -> tuple[list[dict], dict]:
    users = []
    preferences = {}
    cat_names = list(CATEGORIES.keys())
    for i in range(n_users):
        user_id = f"U{i:05d}"
        n_pref = rng.choice([1, 1, 2, 2, 3])
        prefs = rng.sample(cat_names, n_pref)
        preferences[user_id] = prefs
        users.append(
            {
                "user_id": user_id,
                "name": fake.name(),
                "email": fake.unique.email(),
                "signup_date": fake.date_between(
                    start_date="-1y", end_date="today"
                ).isoformat(),
            }
        )
    return users, preferences


# ---------------------------------------------------------------------------
# 4. GENERATOR EVENTS & ORDERS (berpola sesuai preferensi)
# ---------------------------------------------------------------------------

EVENT_TYPES_WEIGHTED = [
    ("search_performed", 0.25),
    ("product_view", 0.35),
    ("product_click", 0.20),
    ("add_to_cart", 0.12),
    ("purchase", 0.08),
]

SEARCH_TEMPLATES = {
    "Sepatu": [
        "sepatu lari ringan",
        "sepatu sneakers pria",
        "sepatu olahraga murah",
        "sepatu anti slip",
    ],
    "Elektronik": [
        "hp murah",
        "laptop ringan",
        "earphone bluetooth",
        "power bank cepat",
    ],
    "Fashion Pria": ["kemeja casual pria", "celana chino slim", "jaket bomber"],
    "Fashion Wanita": ["dress korean style", "atasan wanita murah", "rok midi elegan"],
    "Peralatan Dapur": [
        "rice cooker hemat listrik",
        "air fryer murah",
        "panci anti lengket",
    ],
    "Perawatan Tubuh": [
        "sunscreen untuk kulit sensitif",
        "serum wajah glowing",
        "shampo anti rontok",
    ],
    "Peralatan Olahraga": [
        "matras yoga portable",
        "dumbbell set rumahan",
        "sepeda lipat murah",
    ],
    "Aksesoris": ["tas selempang pria", "jam tangan minimalis", "dompet kulit asli"],
}


def weighted_choice(rng: random.Random, weighted: list[tuple[str, float]]) -> str:
    total = sum(w for _, w in weighted)
    r = rng.uniform(0, total)
    upto = 0
    for item, w in weighted:
        upto += w
        if upto >= r:
            return item
    return weighted[-1][0]


def generate_events_and_orders(
    products: list[dict],
    users: list[dict],
    preferences: dict,
    rng: random.Random,
    avg_events_per_user: int = 40,
):
    products_by_category: dict[str, list[dict]] = {}
    for p in products:
        products_by_category.setdefault(p["category"], []).append(p)

    events = []
    orders = []
    event_id = 0
    order_id = 0

    for user in users:
        uid = user["user_id"]
        prefs = preferences[uid]
        n_events = max(3, int(rng.gauss(avg_events_per_user, 12)))

        for _ in range(n_events):
            # 80% interaksi user mengikuti kategori favoritnya, 20% eksplorasi
            # kategori lain -- ini mensimulasikan perilaku nyata: orang
            # punya minat dominan tapi tetap kadang melihat hal baru.
            if rng.random() < 0.8:
                cat = rng.choice(prefs)
            else:
                cat = rng.choice(list(CATEGORIES.keys()))

            candidate_products = products_by_category[cat]
            product = rng.choice(candidate_products)
            event_type = weighted_choice(rng, EVENT_TYPES_WEIGHTED)

            event = {
                "event_id": event_id,
                "user_id": uid,
                "event_type": event_type,
                "product_id": (
                    product["product_id"] if event_type != "search_performed" else None
                ),
                "search_query": (
                    rng.choice(SEARCH_TEMPLATES[cat])
                    if event_type == "search_performed"
                    else None
                ),
                "timestamp": fake.date_time_between(
                    start_date="-90d", end_date="now"
                ).isoformat(),
            }
            events.append(event)
            event_id += 1

            if event_type == "purchase":
                orders.append(
                    {
                        "order_id": order_id,
                        "user_id": uid,
                        "product_id": product["product_id"],
                        "quantity": rng.randint(1, 3),
                        "total_price": product["price"] * rng.randint(1, 3),
                        "order_date": event["timestamp"],
                    }
                )
                order_id += 1

    return events, orders


# ---------------------------------------------------------------------------
# 5. MAIN
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Generate dataset e-commerce sintetis."
    )
    parser.add_argument("--n-products", type=int, default=5000)
    parser.add_argument("--n-users", type=int, default=500)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out-dir", type=str, default="../../data/raw")
    args = parser.parse_args()

    rng = random.Random(args.seed)
    Faker.seed(args.seed)

    print(f"[1/4] Generating {args.n_products} products...")
    products = generate_products(args.n_products, rng)

    print(f"[2/4] Generating {args.n_users} users...")
    users, preferences = generate_users(args.n_users, rng)

    print("[3/4] Generating events & orders (berpola sesuai preferensi user)...")
    events, orders = generate_events_and_orders(products, users, preferences, rng)

    print("[4/4] Writing to disk...")
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(out_dir / "products.json", "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    with open(out_dir / "users.json", "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)
    with open(out_dir / "events.json", "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=2)
    with open(out_dir / "orders.json", "w", encoding="utf-8") as f:
        json.dump(orders, f, ensure_ascii=False, indent=2)

    print(
        f"Done. {len(products)} products, {len(users)} users, "
        f"{len(events)} events, {len(orders)} orders -> {out_dir}"
    )


if __name__ == "__main__":
    main()
