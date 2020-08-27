all: build

build:
	docker build -t registry.condensat.space/crypto-ssm-tor:0.1.0 .

deploy: build
	cat $(REGISTRY_PASSWORD) | docker login registry.condensat.space --username condensat --password-stdin
	docker push registry.condensat.space/crypto-ssm-tor:0.1.0

start:
	mkdir -p ssm-service && chmod 700 ssm-service
	docker-compose up -d

stop:
	docker-compose down

restart: stop start

logs:
	docker-compose logs -f

.PHONY: build deploy start stop restart log
