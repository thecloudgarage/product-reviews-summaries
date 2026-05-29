import json
import pika
from kafka import KafkaConsumer
from common.utils import env, from_json_bytes, logger

log = logger("kafka_rabbitmq_relay")

BOOTSTRAP = env("KAFKA_BOOTSTRAP_SERVERS", required=True)
TOPIC = env("TOPIC_PRODUCT_REVIEW_BATCHES", "product-review-batches")
GROUP_ID = env("GROUP_ID", "kafka-rabbitmq-relay")

RABBITMQ_HOST = env("RABBITMQ_HOST", required=True)
RABBITMQ_PORT = int(env("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = env("RABBITMQ_USER", "guest")
RABBITMQ_PASSWORD = env("RABBITMQ_PASSWORD", "guest")
QUEUE = env("QUEUE_REVIEW_SUMMARIZATION", "review_summarization_jobs")

def open_rabbit():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
    conn = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT, credentials=credentials)
    )
    channel = conn.channel()
    channel.queue_declare(queue=QUEUE, durable=True)
    return conn, channel

def main():
    conn, ch = open_rabbit()
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=BOOTSTRAP,
        group_id=GROUP_ID,
        auto_offset_reset="earliest",
        enable_auto_commit=False,
        value_deserializer=from_json_bytes,
    )

    while True:
        records = consumer.poll(timeout_ms=1000)
        for _, messages in records.items():
            for msg in messages:
                body = json.dumps(msg.value).encode("utf-8")
                ch.basic_publish(
                    exchange="",
                    routing_key=QUEUE,
                    body=body,
                    properties=pika.BasicProperties(delivery_mode=2),
                )
                log.info("Forwarded product batch for product_id=%s", msg.value["product_id"])
        consumer.commit()

if __name__ == "__main__":
    main()
