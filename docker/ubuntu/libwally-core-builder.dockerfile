FROM ubuntu:bionic

ARG LIBWALLY_CORE_VERSION=0.7.8

RUN apt-get update && apt-get install -y git
RUN git clone https://github.com/ElementsProject/libwally-core.git -b release_${LIBWALLY_CORE_VERSION} /src/libwally


WORKDIR /src/libwally
RUN contrib/ubuntu_deps.sh
