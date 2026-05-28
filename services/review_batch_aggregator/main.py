import json
import time
from collections import defaultdict
from kafka import KafkaConsumer, KafkaProducer
from common.utils import env, from_json_bytes, logger, now_iso

log = logger("review_batch_aggregator")

BOOTSTRAP = env("KAFKA_BOOTSTRAP_SERVERS", required=True)
IN_TOPIC = env("TOPIC_PRODUCT_REVIEWS", "product-reviews")
OUT_TOPIC = env("TOPIC_PRODUCT_REVIEW_BATCHES", "product-review-batches")
GROUP_ID = env("GROUP_ID", "review-batch-aggregator")
WINDOW_SECONDS = int(env("WINDOW_SECONDS", "60"))
MAX_BATCH_SIZE = int(env("MAX_BATCH_SIZE", "20"))

def emit_batches(producer: KafkaProducer, grouped):
    for product_id, reviews in grouped.items():
        if not reviews:
            continue
        payload = {
            "product_id": product_id,
            "category": reviews[0]["category"],
            "window_closed_at": now_iso(),
            "review_count": len(reviews),
            "reviews": reviews,
        }
        producer.send(
            OUT_TOPIC,
            key=product_id.encode("utf-8"),
            value=json.dumps(payload).encode("utf-8")
        )
    producer.flush()

def main():
    consumer = KafkaConsumer(
        IN_TOPIC,
        bootstrap_servers=BOOTSTRAP,
        group_id=GROUP_ID,
        auto_offset_reset="earliest",
        enable_auto_commit=False,
        value_deserializer=from_json_bytes,
    )
    producer = KafkaProducer(bootstrap_servers=BOOTSTRAP, acks="all", retries=5)

    grouped = defaultdict(list)
    started = time.time()

    while True:
        records = consumer.poll(timeout_ms=1000)
        for _, messages in records.items():
            for msg in messages:
                review = msg.value
                grouped[review["product_id"]].append(review)

        flush_due_time = (time.time() - started) >= WINDOW_SECONDS
        flush_due_size = any(len(v) >= MAX_BATCH_SIZE for v in grouped.values())

        if grouped and (flush_due_time or flush_due_size):
            emit_batches(producer, grouped)
            consumer.commit()
            log.info("Emitted %s review batches", len(grouped))
            grouped.clear()
            started = time.time()

if __name__ == "__main__":
    main()
