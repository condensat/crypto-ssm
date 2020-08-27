ARG LIBWALLY_CORE_VERSION

FROM wallycore:${LIBWALLY_CORE_VERSION}-ubuntu

RUN apt-get update -yy &&\
    apt-get install -yy --no-install-recommends python3.8-minimal libpython3.8 python3-pip wget &&\
    apt-get -yy autoremove &&\
    apt-get -yy clean &&\
    rm -rf /var/lib/apt/lists/* /var/cache/* /tmp/* /usr/share/locale/* /usr/share/man /usr/share/doc /lib/xtables/libip6*

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8 

# requirements
ENV PYTHONPATH='/usr/local/lib/python3.8/site-packages'
COPY server/requirements.txt /ssm-server/requirements.txt
RUN [ "python3", "-m", "pip", "install", "-r", "/ssm-server/requirements.txt" ]

COPY ssm /ssm-server/ssm
COPY server /ssm-server/server

ENV PYTHONPATH "${PYTHONPATH}:/ssm-server"
CMD [ "python3", "/ssm-server/server/server.py" ]
