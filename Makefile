.DEFAULT_GOAL := build
LIBWALLY_VERSION?=0.7.8
CRYPTO_SSM_VERSION?=0.1.0
REGISTRY_PASSWORD?=condensat
#BITCOIN_VERSION?=0.20.0
#ELEMENTS_VERSION?=0.18.1.8

builder:
	docker build -f docker/ubuntu/libwally-core-builder.dockerfile --build-arg=LIBWALLY_CORE_VERSION=$(LIBWALLY_VERSION) . -t libwally-core-builder:$(LIBWALLY_VERSION)-ubuntu

libwally-core: builder
	docker build -f docker/ubuntu/libwally-core.dockerfile --build-arg=LIBWALLY_CORE_VERSION=$(LIBWALLY_VERSION) . -t libwally-core:$(LIBWALLY_VERSION)-ubuntu

wallycore: builder
	docker build -f docker/ubuntu/wallycore.dockerfile --build-arg=LIBWALLY_CORE_VERSION=$(LIBWALLY_VERSION) . -t wallycore:$(LIBWALLY_VERSION)-ubuntu

crypto-ssm: wallycore
	docker build -f docker/ubuntu/crypto-ssm.dockerfile --build-arg=LIBWALLY_CORE_VERSION=$(LIBWALLY_VERSION) . -t crypto-ssm:$(LIBWALLY_VERSION)-ubuntu
	docker volume create ssm-keys

start: crypto-ssm
	docker run -ti --rm --mount source=ssm-keys,target=/ssm-keys crypto-ssm:$(LIBWALLY_VERSION)-ubuntu

server: crypto-ssm
	# docker run -ti --rm -p 5000:5000 crypto-ssm:$(LIBWALLY_VERSION)-ubuntu python3 /crypto-ssm/server/server.py
	docker run -ti --rm --mount source=ssm-keys,target=/ssm-keys -p 5000:5000 crypto-ssm:$(LIBWALLY_VERSION)-ubuntu python3 /crypto-ssm/server/server.py

test: crypto-ssm
	docker run -t --rm -w /crypto-ssm crypto-ssm:$(LIBWALLY_VERSION)-ubuntu pytest

build: libwally-core wallycore crypto-ssm

deploy:
	docker tag crypto-ssm:$(LIBWALLY_VERSION)-ubuntu registry.condensat.space/crypto-ssm:$(CRYPTO_SSM_VERSION)
	cat $(REGISTRY_PASSWORD) | docker login registry.condensat.space --username condensat --password-stdin
	docker push registry.condensat.space/crypto-ssm:$(CRYPTO_SSM_VERSION)

clean:
	docker rmi -f wallycore:$(LIBWALLY_VERSION)-ubuntu libwally-core:$(LIBWALLY_VERSION)-ubuntu libwally-core-builder:$(LIBWALLY_VERSION)-ubuntu

deep-clean:
	yes | docker system prune --all

.PHONY: build clean start builder libwally-core wallycore test
