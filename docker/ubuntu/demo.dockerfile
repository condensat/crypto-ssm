ARG LIBWALLY_CORE_VERSION=0.7.7

FROM wallycore:${LIBWALLY_CORE_VERSION}-ubuntu

RUN apt-get update -yy &&\
    apt-get install -yy --no-install-recommends python3.6-minimal libpython3.6 python3-pip wget &&\
    apt-get -yy autoremove &&\
    apt-get -yy clean &&\
    rm -rf /var/lib/apt/lists/* /var/cache/* /tmp/* /usr/share/locale/* /usr/share/man /usr/share/doc /lib/xtables/libip6*

COPY demo/ /demo

ENV BITCOIN_VERSION=0.19.1

ENV ELEMENTS_VERSION=0.18.1.6

RUN [ "/bin/bash", "-c", "/demo/scripts/bitcoin-elements-simple.sh" ]

ENV PYTHONPATH='/usr/local/lib/python3.6/site-packages'

RUN [ "python3.6m", "-m", "pip", "install", "-r", "/demo/requirements.txt" ]

COPY cli/ /cli

COPY src/ /cli/src

CMD [ "/bin/bash" ]
