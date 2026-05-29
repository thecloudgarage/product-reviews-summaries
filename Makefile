SERVICES := product_seeder review_producer ratings_aggregator review_batch_aggregator kafka_rabbitmq_relay llm_summarizer_worker recommendation_service product_api

DOCKERHUB_REPO ?= thecloudgarage
TAG ?= latest

.PHONY: build topics

build:
    @for svc in $(SERVICES); do \
        docker build \
            -f services/$$svc/Dockerfile \
            --build-arg DOCKERHUB_REPO=$(DOCKERHUB_REPO) \
            -t $(DOCKERHUB_REPO)/$$svc:$(TAG) . ; \
    done
    docker build \
        -f web/frontend/Dockerfile \
        --build-arg DOCKERHUB_REPO=$(DOCKERHUB_REPO) \
        -t $(DOCKERHUB_REPO)/frontend:$(TAG) .

topics:
    chmod +x scripts/create-topics.sh
    ./scripts/create-topics.sh
