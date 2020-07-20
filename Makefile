.DEFAULT_GOAL := build
LIBWALLY_VERSION?=0.7.8
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

start: crypto-ssm
	docker run -ti --rm crypto-ssm:$(LIBWALLY_VERSION)-ubuntu

test: crypto-ssm
	docker run -t --rm -w /crypto-ssm crypto-ssm:$(LIBWALLY_VERSION)-ubuntu pytest

build: libwally-core wallycore

clean:
	docker rmi -f wallycore:$(LIBWALLY_VERSION)-ubuntu libwally-core:$(LIBWALLY_VERSION)-ubuntu libwally-core-builder:$(LIBWALLY_VERSION)-ubuntu

.PHONY: build clean start builder libwally-core wallycore test
