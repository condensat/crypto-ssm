ARG LIBWALLY_CORE_VERSION

FROM wallycore:${LIBWALLY_CORE_VERSION}-ubuntu

RUN apt-get update -yy &&\
    apt-get install -yy --no-install-recommends python3.6-minimal libpython3.6 python3-pip wget &&\
    apt-get -yy autoremove &&\
    apt-get -yy clean &&\
    rm -rf /var/lib/apt/lists/* /var/cache/* /tmp/* /usr/share/locale/* /usr/share/man /usr/share/doc /lib/xtables/libip6*

ARG BITCOIN_VERSION=0.19.1

ARG ELEMENTS_VERSION=0.18.1.6

ENV LC_ALL=C.UTF-8

ENV LANG=C.UTF-8 

COPY demo/ /demo

RUN [ "/bin/bash", "-c", "/demo/scripts/bitcoin-elements-simple.sh" ]

ENV PYTHONPATH='/usr/local/lib/python3.6/site-packages'

RUN [ "python3.6m", "-m", "pip", "install", "-r", "/demo/requirements.txt" ]

COPY ssm /crypto-ssm/ssm
COPY cli /crypto-ssm/cli
COPY test /crypto-ssm/test

COPY setup.py /crypto-ssm

RUN [ "python3.6m", "-m", "pip", "install", "/crypto-ssm" ]

CMD [ "/bin/bash" ]
