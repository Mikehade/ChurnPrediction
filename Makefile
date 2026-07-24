IMAGE_NAME := churn-api
CONTAINER_NAME := churn-api
PORT := 8000

.PHONY: build run start stop logs shell clean run-local

build:
	docker build -t $(IMAGE_NAME) .

run:
	docker rm -f $(CONTAINER_NAME) >/dev/null 2>&1 || true
	docker run -d \
		--name $(CONTAINER_NAME) \
		-p $(PORT):8000 \
		$(IMAGE_NAME)

start: build run

stop:
	docker stop $(CONTAINER_NAME) || true
	docker rm $(CONTAINER_NAME) || true

logs:
	docker logs -f $(CONTAINER_NAME)

shell:
	docker exec -it $(CONTAINER_NAME) /bin/bash

clean:
	docker rm -f $(CONTAINER_NAME) >/dev/null 2>&1 || true
	docker rmi $(IMAGE_NAME) || true

run-local:
	python main.py