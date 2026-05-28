import json
import logging
import math
import os
import random
import string
from datetime import datetime, timezone
from typing import Any, Dict, List

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

def logger(name: str):
    return logging.getLogger(name)

def env(name: str, default=None, required: bool = False):
    value = os.getenv(name, default)
    if required and value is None:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def rand_id(prefix: str, n: int = 8) -> str:
    chars = string.ascii_lowercase + string.digits
    return f"{prefix}-" + "".join(random.choices(chars, k=n))

def to_json_bytes(value: Dict[str, Any]) -> bytes:
    return json.dumps(value, ensure_ascii=False).encode("utf-8")

def from_json_bytes(value: bytes) -> Dict[str, Any]:
    return json.loads(value.decode("utf-8"))

CATEGORIES: List[str] = [
    "Laptops",
    "Monitors",
    "Servers",
    "Storage",
    "Accessories",
    "Networking",
    "Desktops",
    "Tablets",
]

ADJECTIVES = ["Ultra", "Pro", "Prime", "Max", "Edge", "Eco", "Flex", "Smart"]
NOUNS = ["Display", "Notebook", "Station", "Array", "Dock", "Hub", "Panel", "Node"]

REVIEW_TITLES = [
    "Excellent overall",
    "Solid value",
    "Good but not perfect",
    "Mixed experience",
    "Highly recommended",
    "Needs improvement",
]

REVIEW_TEXTS = [
    "Excellent performance and very reliable.",
    "Good value for the price and easy to use.",
    "Strong build quality and consistent day to day usage.",
    "I like the features, but setup could be simpler.",
    "Great performance, though thermals could be better.",
    "Stable under load and fits well into the current environment.",
    "User experience is clean, but updates could be smoother.",
    "Exceeded expectations for the price point.",
    "Not bad overall, but support documentation could improve.",
    "Fast deployment and solid performance in production-like tests."
]

def fake_product(i: int) -> Dict[str, Any]:
    category = random.choice(CATEGORIES)
    name = f"{random.choice(ADJECTIVES)} {random.choice(NOUNS)} {i}"
    return {
        "product_id": f"P-{i:04d}",
        "name": name,
        "category": category,
        "brand": "Dell",
        "price": round(random.uniform(49.0, 3999.0), 2),
        "description": f"Synthetic {category} product {i}",
        "avg_rating": 0.0,
        "rating_count": 0,
        "rating_sum": 0.0,
        "updated_at": now_iso(),
    }

def fake_review(product: Dict[str, Any]) -> Dict[str, Any]:
    rating = random.choices([1, 2, 3, 4, 5], weights=[0.06, 0.10, 0.19, 0.32, 0.33], k=1)[0]
    return {
        "review_id": rand_id("R"),
        "product_id": product["product_id"],
        "category": product["category"],
        "rating": rating,
        "review_title": random.choice(REVIEW_TITLES),
        "review_text": random.choice(REVIEW_TEXTS),
        "reviewer_alias": rand_id("user", 5),
        "event_ts": now_iso(),
    }

def compute_score(avg_rating: float, rating_count: int) -> float:
    return (avg_rating * 0.8) + (math.log10(rating_count + 1) * 0.2)
