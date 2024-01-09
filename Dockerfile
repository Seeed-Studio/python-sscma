
FROM --platform=$BUILDPLATFORM ghcr.io/hassio-addons/base:15.0.3 as builder

WORKDIR /tmp

COPY . /tmp

RUN apk add --no-cache --update python3 py3-pip py3-wheel && \
    python3 setup.py bdist_wheel


FROM --platform=$BUILDPLATFORM ghcr.io/hassio-addons/base:15.0.3

WORKDIR /tmp

COPY --from=builder /tmp/dist/*.whl /tmp/dist/

RUN apk add --no-cache --update python3 py3-pip \
        py3-setuptools py3-opencv py3-scipy py3-numpy \
        py3-matplotlib py3-yaml py3-pillow py3-click py3-tqdm \
        py3-paho-mqtt py3-pyserial && \
    SUPERVISION_VERSION=$(curl -s https://api.github.com/repos/roboflow/supervision/releases/latest | grep "tag_name" | awk '{print substr($2, 2, length($2)-3)}') && \
    wget https://github.com/roboflow/supervision/archive/refs/tags/${SUPERVISION_VERSION}.zip && \
    unzip ${SUPERVISION_VERSION}.zip -d /usr/local && \
    rm -fr ${SUPERVISION_VERSION}.zip && \
    cd /usr/local/supervision-${SUPERVISION_VERSION} && \
    python3 -m pip install -e . --break-system-packages --no-deps && \
    python3 -m pip install --no-cache-dir --break-system-packages xmodem && \
    python3 -m pip install --no-cache-dir --break-system-packages /tmp/dist/*.whl && \
    rm -fr /tmp/*

ENTRYPOINT ["sscma.cli"]
