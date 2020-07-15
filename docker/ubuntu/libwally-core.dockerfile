# ARG LIBWALLY_CORE_VERSION=0.7.8

FROM libwally-core-builder:${LIBWALLY_CORE_VERSION}-ubuntu AS builder

## build libwally
RUN ./tools/autogen.sh

ENV PYTHON_VERSION=3
RUN ./configure --prefix=/stage/local --enable-elements --enable-static --enable-shared

RUN make &&\
    make check &&\
    make install


FROM ubuntu:bionic

COPY --from=builder /stage/local /usr/local
