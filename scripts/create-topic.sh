#!/usr/bin/env bash
set -euo pipefail

BOOTSTRAP="${KAFKA_BOOTSTRAP_SERVERS:-kafka.confluent.svc.cluster.local:9092}"

POD=$(kubectl -n confluent get pods -l app=kafka -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || true)
if [ -z "${POD}" ]; then
  POD=$(kubectl -n confluent get pods | awk '/kafka-/{print $1; exit}')
fi

if [ -z "${POD}" ]; then
  echo "Could not find Kafka broker pod in namespace confluent"
  exit 1
fi

kubectl -n confluent exec -it "${POD}" -- bash -lc "
kafka-topics --bootstrap-server ${BOOTSTRAP} --create --if-not-exists --topic product-reviews --partitions 6 --replication-factor 3
kafka-topics --bootstrap-server ${BOOTSTRAP} --create --if-not-exists --topic product-review-batches --partitions 6 --replication-factor 3
kafka-topics --bootstrap-server ${BOOTSTRAP} --create --if-not-exists --topic product-review-dlq --partitions 3 --replication-factor 3
kafka-topics --bootstrap-server ${BOOTSTRAP} --create --if-not-exists --topic product-review-batches-dlq --partitions 3 --replication-factor 3
