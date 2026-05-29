from elasticsearch import helpers
from common.utils import build_elasticsearch_client, env, fake_product, logger

log = logger("product_seeder")

PRODUCTS_INDEX = env("PRODUCTS_INDEX", "products")
COUNT = int(env("PRODUCT_COUNT", "500"))

def ensure_products_index(es):
    if es.indices.exists(index=PRODUCTS_INDEX):
        log.info("Index %s already exists", PRODUCTS_INDEX)
        return

    es.indices.create(
        index=PRODUCTS_INDEX,
        mappings={
            "properties": {
                "product_id": {"type": "keyword"},
                "name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                "category": {"type": "keyword"},
                "brand": {"type": "keyword"},
                "price": {"type": "float"},
                "description": {"type": "text"},
                "avg_rating": {"type": "float"},
                "rating_count": {"type": "integer"},
                "rating_sum": {"type": "float"},
                "updated_at": {"type": "date"},
            }
        }
    )
    log.info("Created index %s", PRODUCTS_INDEX)

def main():
    es = build_elasticsearch_client()
    ensure_products_index(es)

    actions = []
    for i in range(1, COUNT + 1):
        product = fake_product(i)
        actions.append({
            "_index": PRODUCTS_INDEX,
            "_id": product["product_id"],
            "_source": product,
        })

    success, _ = helpers.bulk(es, actions, refresh="wait_for")
    log.info("Seeded %s products", success)

if __name__ == "__main__":
    main()
