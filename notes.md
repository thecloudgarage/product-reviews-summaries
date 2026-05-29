```
kubectl scale statefulset kafka -n confluent --replicas=0
```
```
#messages from product review batches topic
{
  "product_id": "P-0228",
  "category": "Monitors",
  "window_closed_at": "2026-05-29T13:31:33.121104+00:00",
  "review_count": 1,
  "reviews": [
    {
      "review_id": "R-fjr9meyj",
      "product_id": "P-0228",
      "category": "Monitors",
      "rating": 4,
      "review_title": "Highly recommended",
      "review_text": "Fast deployment and solid performance in production-like tests.",
      "reviewer_alias": "user-gnrlp",
      "event_ts": "2026-05-29T13:31:06.662000+00:00"
    }
  ]
}
```
