.DEFAULT_GOAL := build

builder:
	docker build -f ubuntu/libwally-core-builder.dockerfile . -t libwally-core-builder:0.7.7-ubuntu

libwally-core: builder
	docker build -f ubuntu/libwally-core.dockerfile . -t libwally-core:0.7.7-ubuntu

wallycore: builder
	docker build -f ubuntu/wallycore.dockerfile . -t wallycore:0.7.7-ubuntu

start: wallycore
	docker run -ti --rm wallycore:0.7.7-ubuntu

build: libwally-core wallycore

clean:
	docker rmi -f wallycore:0.7.7-ubuntu libwally-core:0.7.7-ubuntu libwally-core-builder:0.7.7-ubuntu

.PHONY: build clean start builder libwally-core wallycore
