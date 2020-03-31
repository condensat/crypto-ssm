ARG LIBWALLY_CORE_VERSION=0.7.7

FROM libwally-core-builder:${LIBWALLY_CORE_VERSION}-ubuntu AS builder

# https://pythonspeed.com/articles/activate-virtualenv-dockerfile/
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m virtualenv --python=/usr/bin/python3 $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# install wallycore
RUN pip install --prefix /stage/local .


FROM ubuntu:bionic

RUN apt-get update &&\
    apt-get install -y --no-install-recommends python3.6-minimal libpython3.6 &&\
    apt-get -y autoremove &&\
    apt-get -y clean &&\
    rm -rf /var/lib/apt/lists/* /var/cache/* /tmp/* /usr/share/locale/* /usr/share/man /usr/share/doc /lib/xtables/libip6*

COPY --from=builder /stage/local /usr/local

ENV PYTHONPATH='/usr/local/lib/python3.6/site-packages'
CMD [ "python3.6m" ]
