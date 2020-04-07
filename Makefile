.DEFAULT_GOAL := build

builder:
	docker build -f docker/ubuntu/libwally-core-builder.dockerfile . -t libwally-core-builder:0.7.7-ubuntu

libwally-core: builder
	docker build -f docker/ubuntu/libwally-core.dockerfile . -t libwally-core:0.7.7-ubuntu

wallycore: builder
	docker build -f docker/ubuntu/wallycore.dockerfile . -t wallycore:0.7.7-ubuntu

demo: wallycore
	docker build -f docker/ubuntu/demo.dockerfile . -t demo:0.7.7-ubuntu

start: demo
	docker run -ti --rm demo:0.7.7-ubuntu

build: libwally-core wallycore

clean:
	docker rmi -f wallycore:0.7.7-ubuntu libwally-core:0.7.7-ubuntu libwally-core-builder:0.7.7-ubuntu

.PHONY: build clean start builder libwally-core wallycore
