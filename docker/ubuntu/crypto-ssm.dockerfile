ARG LIBWALLY_CORE_VERSION

FROM wallycore:${LIBWALLY_CORE_VERSION}-ubuntu

RUN apt-get update -yy &&\
    apt-get install -yy --no-install-recommends python3.8-minimal libpython3.8 python3-pip wget &&\
    apt-get -yy autoremove &&\
    apt-get -yy clean &&\
    rm -rf /var/lib/apt/lists/* /var/cache/* /tmp/* /usr/share/locale/* /usr/share/man /usr/share/doc /lib/xtables/libip6*

#ARG BITCOIN_VERSION=0.19.1

#ARG ELEMENTS_VERSION=0.18.1.6

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8 

#COPY demo/scripts/bitcoin-elements-simple.sh /crypto-ssm/scripts/bitcoin-elements-simple.sh
#RUN [ "/bin/bash", "-c", "/crypto-ssm/scripts/bitcoin-elements-simple.sh" ]

# requirements
ENV PYTHONPATH='/usr/local/lib/python3.8/site-packages'

COPY requirements.txt /crypto-ssm/requirements.txt
RUN [ "python3", "-m", "pip", "install", "-r", "/crypto-ssm/requirements.txt" ]

COPY ssm /crypto-ssm/ssm
COPY cli /crypto-ssm/cli
COPY test /crypto-ssm/test

COPY setup.py /crypto-ssm

RUN [ "python3", "-m", "pip", "install", "/crypto-ssm" ]

CMD [ "/bin/bash" ]
