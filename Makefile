SERVICES=product_seeder review_producer ratings_aggregator review_batch_aggregator kafka_rabbitmq_relay llm_summarizer_worker recommendation_service product_api

build:
	docker build -f services/product_seeder/Dockerfile -t product_seeder:latest .
	docker build -f services/review_producer/Dockerfile -t review_producer:latest .
	docker build -f services/ratings_aggregator/Dockerfile -t ratings_aggregator:latest .
	docker build -f services/review_batch_aggregator/Dockerfile -t review_batch_aggregator:latest .
	docker build -f services/kafka_rabbitmq_relay/Dockerfile -t kafka_rabbitmq_relay:latest .
	docker build -f services/llm_summarizer_worker/Dockerfile -t llm_summarizer_worker:latest .
	docker build -f services/recommendation_service/Dockerfile -t recommendation_service:latest .
	docker build -f services/product_api/Dockerfile -t product_api:latest .
	docker build -f web/frontend/Dockerfile -t frontend:latest .

topics:
	chmod +x scripts/create-topics.sh
	./scripts/create-topics.sh
