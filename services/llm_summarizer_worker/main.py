import json
import pika
import redis
from common.utils import env, logger, now_iso

log = logger("llm_summarizer_worker")

RABBITMQ_HOST = env("RABBITMQ_HOST", required=True)
RABBITMQ_PORT = int(env("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = env("RABBITMQ_USER", "guest")
RABBITMQ_PASSWORD = env("RABBITMQ_PASSWORD", "guest")
QUEUE = env("QUEUE_REVIEW_SUMMARIZATION", "review_summarization_jobs")

REDIS_URL = env("REDIS_URL", required=True)

USE_FAKE_LLM = env("USE_FAKE_LLM", "true").lower() == "true"
OPENAI_API_KEY = env("OPENAI_API_KEY", "")
OPENAI_MODEL = env("OPENAI_MODEL", "gpt-4o-mini")

r = redis.from_url(REDIS_URL, decode_responses=True)

def summarize_fake(reviews):
    positives = [rv["review_text"] for rv in reviews if rv["rating"] >= 4][:3]
    negatives = [rv["review_text"] for rv in reviews if rv["rating"] <= 2][:3]
    avg = sum(float(r["rating"]) for r in reviews) / max(len(reviews), 1)

    return {
        "summary": f"Average rating is {avg:.2f}/5 based on {len(reviews)} reviews.",
        "highlights": positives,
        "concerns": negatives,
    }

def summarize_llm(reviews):
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
    prompt = (
        "Summarize these product reviews as JSON with keys: summary, highlights, concerns.\n"
        f"Reviews: {json.dumps(reviews)}"
    )
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    text = response.choices[0].message.content
    try:
        return json.loads(text)
    except Exception:
        return {"summary": text, "highlights": [], "concerns": []}

def callback(ch, method, properties, body):
    payload = json.loads(body.decode("utf-8"))
    product_id = payload["product_id"]
    reviews = payload["reviews"]

    result = summarize_fake(reviews) if USE_FAKE_LLM else summarize_llm(reviews)

    stored = {
        "product_id": product_id,
        "category": payload["category"],
        "review_count": len(reviews),
        "generated_at": now_iso(),
        "summary": result.get("summary"),
        "highlights": result.get("highlights", []),
        "concerns": result.get("concerns", []),
    }

    r.set(f"summary:{product_id}", json.dumps(stored))
    ch.basic_ack(delivery_tag=method.delivery_tag)
    log.info("Stored summary for product_id=%s", product_id)

def main():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT, credentials=credentials)
    )
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE, on_message_callback=callback)
    log.info("Waiting for summarization jobs")
    channel.start_consuming()

if __name__ == "__main__":
    main()
