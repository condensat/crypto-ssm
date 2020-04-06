ARG LIBWALLY_CORE_VERSION=0.7.7

FROM libwally-core-builder:${LIBWALLY_CORE_VERSION}-ubuntu AS builder

# https://pythonspeed.com/articles/activate-virtualenv-dockerfile/
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m virtualenv --python=/usr/bin/python3 $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# install wallycore
RUN pip install --prefix /stage/local .

FROM ubuntu:bionic

COPY --from=builder /stage/local /usr/local

COPY demo/ /demo


ENV BITCOIN_VERSION=0.19.1

ENV ELEMENTS_VERSION=0.18.1.6

RUN apt-get update -yy &&\
    apt-get install -yy --no-install-recommends python3.6-minimal libpython3.6 python3-pip wget &&\
    apt-get -yy autoremove &&\
    apt-get -yy clean &&\
    rm -rf /var/lib/apt/lists/* /var/cache/* /tmp/* /usr/share/locale/* /usr/share/man /usr/share/doc /lib/xtables/libip6*

RUN [ "/bin/bash", "-c", "/demo/scripts/bitcoin-elements-simple.sh" ]

ENV PYTHONPATH='/usr/local/lib/python3.6/site-packages'

RUN [ "python3.6m", "-m", "pip", "install", "-r", "/demo/requirements.txt" ]

CMD [ "/bin/bash", "/demo/scripts/launch.sh" ]