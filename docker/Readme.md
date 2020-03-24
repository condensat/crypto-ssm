# Docker images

Images are base on ubuntu (bionic).
Default version is `0.7.7`.
  > --build-args LIBWALLY_CORE_VERSION=0.7.7

## Builder image

Contains the build environement for libwally-core with source.

  > build -f ubuntu/libwally-core.dockerfile . -t libwally-core:0.7.7-ubuntu

## Native libraries

  > docker build -f ubuntu/libwally-core.dockerfile . -t libwally-core:0.7.7-ubuntu

## Python binding

  > docker build -f ubuntu/wallycore.dockerfile . -t wallycore:0.7.7-ubuntu

## Using docker image

### Python (wallycore)

Run interactive python interpreter

  > docker run -ti --rm wallycore:0.7.7-ubuntu

## TL;DR

> make && make start
