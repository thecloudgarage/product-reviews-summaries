import time
from collections import defaultdict
from kafka import KafkaConsumer
from elasticsearch import Elasticsearch
from common.utils import env, from_json_bytes, logger, now_iso

log = logger("ratings_aggregator")

BOOTSTRAP = env("KAFKA_BOOTSTRAP_SERVERS", required=True)
TOPIC = env("TOPIC_PRODUCT_REVIEWS", "product-reviews")
GROUP_ID = env("GROUP_ID", "ratings-aggregator")
ES_URL = env("ELASTICSEARCH_URL", required=True)
PRODUCTS_INDEX = env("PRODUCTS_INDEX", "products")
WINDOW_SECONDS = int(env("WINDOW_SECONDS", "60"))

def flush_batch(es: Elasticsearch, batch):
    for product_id, stats in batch.items():
        es.update(
            index=PRODUCTS_INDEX,
            id=product_id,
            scripted_upsert=True,
            script={
                "source": """
                    if (ctx._source.rating_sum == null) { ctx._source.rating_sum = 0.0; }
                    if (ctx._source.rating_count == null) { ctx._source.rating_count = 0; }
                    ctx._source.rating_sum += params.rating_sum;
                    ctx._source.rating_count += params.rating_count;
                    ctx._source.avg_rating = ctx._source.rating_sum / ctx._source.rating_count;
                    ctx._source.updated_at = params.updated_at;
                """,
                "params": {
                    "rating_sum": stats["rating_sum"],
                    "rating_count": stats["rating_count"],
                    "updated_at": now_iso(),
                },
            },
            upsert={
                "product_id": product_id,
                "avg_rating": stats["rating_sum"] / max(stats["rating_count"], 1),
                "rating_sum": stats["rating_sum"],
                "rating_count": stats["rating_count"],
                "updated_at": now_iso(),
            }
        )
    log.info("Flushed %s product aggregates", len(batch))

def main():
    es = Elasticsearch(ES_URL)
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=BOOTSTRAP,
        group_id=GROUP_ID,
        enable_auto_commit=False,
        auto_offset_reset="earliest",
        value_deserializer=from_json_bytes,
    )

    batch = defaultdict(lambda: {"rating_sum": 0.0, "rating_count": 0})
    window_start = time.time()

    while True:
        records = consumer.poll(timeout_ms=1000)
        for _, messages in records.items():
            for msg in messages:
                review = msg.value
                product_id = review["product_id"]
                batch[product_id]["rating_sum"] += float(review["rating"])
                batch[product_id]["rating_count"] += 1

        if time.time() - window_start >= WINDOW_SECONDS and batch:
            flush_batch(es, batch)
            consumer.commit()
            batch.clear()
            window_start = time.time()

if __name__ == "__main__":
    main()
