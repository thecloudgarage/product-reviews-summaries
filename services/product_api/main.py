import json
from fastapi import FastAPI, HTTPException
from elasticsearch import Elasticsearch
import redis
from common.utils import env

app = FastAPI(title="product-api")

ES = Elasticsearch(env("ELASTICSEARCH_URL", required=True))
REDIS = redis.from_url(env("REDIS_URL", required=True), decode_responses=True)
PRODUCTS_INDEX = env("PRODUCTS_INDEX", "products")
REVIEWS_INDEX = env("REVIEWS_INDEX", "product_reviews")

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/api/categories")
def categories():
    res = ES.search(
        index=PRODUCTS_INDEX,
        size=0,
        aggs={"categories": {"terms": {"field": "category", "size": 100}}}
    )
    return [bucket["key"] for bucket in res["aggregations"]["categories"]["buckets"]]

@app.get("/api/categories/top3")
def top3_by_category():
    cats = categories()
    out = {}
    for category in cats:
        rows = REDIS.zrevrange(f"top3:{category}", 0, 2, withscores=True)
        out[category] = [{"product_id": row[0], "score": row[1]} for row in rows]
    return out

@app.get("/api/categories/{category}/products")
def products_by_category(category: str):
    res = ES.search(
        index=PRODUCTS_INDEX,
        size=500,
        sort=[{"avg_rating": "desc"}],
        query={"term": {"category": category}},
    )
    return [hit["_source"] for hit in res["hits"]["hits"]]

@app.get("/api/products/{product_id}")
def product(product_id: str):
    try:
        return ES.get(index=PRODUCTS_INDEX, id=product_id)["_source"]
    except Exception:
        raise HTTPException(status_code=404, detail="Product not found")

@app.get("/api/products/{product_id}/reviews")
def product_reviews(product_id: str):
    res = ES.search(
        index=REVIEWS_INDEX,
        size=100,
        sort=[{"event_ts": "desc"}],
        query={"term": {"product_id": product_id}},
    )
    return [hit["_source"] for hit in res["hits"]["hits"]]

@app.get("/api/products/{product_id}/summary")
def product_summary(product_id: str):
    raw = REDIS.get(f"summary:{product_id}")
    if not raw:
        return {"product_id": product_id, "summary": None, "highlights": [], "concerns": []}
    return json.loads(raw)
