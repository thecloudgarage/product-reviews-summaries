import random
import time
from kafka import KafkaProducer
from common.utils import build_elasticsearch_client, env, fake_review, logger, to_json_bytes

log = logger("review_producer")

PRODUCTS_INDEX = env("PRODUCTS_INDEX", "products")
BOOTSTRAP = env("KAFKA_BOOTSTRAP_SERVERS", required=True)
TOPIC = env("TOPIC_PRODUCT_REVIEWS", "product-reviews")
INTERVAL = float(env("PRODUCE_INTERVAL_SECONDS", "1"))

def load_products(es):
    res = es.search(index=PRODUCTS_INDEX, size=1000, query={"match_all": {}})
    return [hit["_source"] for hit in res["hits"]["hits"]]

def main():
    es = build_elasticsearch_client()
    products = load_products(es)
    if not products:
        raise RuntimeError("No products found. Run product_seeder first.")

    producer = KafkaProducer(
        bootstrap_servers=BOOTSTRAP,
        key_serializer=lambda k: k.encode("utf-8"),
        value_serializer=lambda v: to_json_bytes(v),
        acks="all",
        retries=5,
    )

    while True:
        product = random.choice(products)
        review = fake_review(product)
        producer.send(TOPIC, key=review["product_id"], value=review)
        producer.flush()
        log.info("Produced review_id=%s product_id=%s rating=%s", review["review_id"], review["product_id"], review["rating"])
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
