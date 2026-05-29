from kafka import KafkaConsumer
from common.utils import build_redis_client, compute_score, env, from_json_bytes, logger

log = logger("recommendation_service")

BOOTSTRAP = env("KAFKA_BOOTSTRAP_SERVERS", required=True)
TOPIC = env("TOPIC_PRODUCT_REVIEWS", "product-reviews")
GROUP_ID = env("GROUP_ID", "recommendation-service")

r = build_redis_client(decode_responses=True)

def trim_top3(zkey: str):
    card = r.zcard(zkey)
    if card > 3:
        r.zremrangebyrank(zkey, 0, card - 4)

def update_score(review):
    product_id = review["product_id"]
    category = review["category"]
    rating = float(review["rating"])

    stats_key = f"stats:{product_id}"
    r.hincrbyfloat(stats_key, "rating_sum", rating)
    r.hincrby(stats_key, "rating_count", 1)
    r.hset(stats_key, "category", category)

    stats = r.hgetall(stats_key)
    rating_sum = float(stats.get("rating_sum", 0))
    rating_count = int(stats.get("rating_count", 0))
    avg_rating = rating_sum / max(rating_count, 1)

    score = compute_score(avg_rating, rating_count)

    zkey = f"top3:{category}"
    r.zadd(zkey, {product_id: score})
    trim_top3(zkey)

    log.info("Updated top3 for category=%s product_id=%s score=%.4f", category, product_id, score)

def main():
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=BOOTSTRAP,
        group_id=GROUP_ID,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        value_deserializer=from_json_bytes,
    )

    for msg in consumer:
        review = msg.value
        update_score(review)

if __name__ == "__main__":
    main()
