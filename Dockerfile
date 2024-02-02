
FROM --platform=$TARGETPLATFORM debian:bookworm-slim as builder

WORKDIR /tmp

COPY . /tmp

RUN set -ex && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 \
        python3-build \
        python3-venv \
        && \
    python3 -m build --sdist && \
    tar -xzf dist/*.tar.gz -C dist && \
    rm dist/*.tar.gz


FROM --platform=$TARGETPLATFORM debian:bookworm-slim

WORKDIR /home

COPY --from=builder /tmp/dist/python-sscma-* /home/python-sscma

RUN set -ex && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-opencv \
        python3-numpy \
        python3-scipy \
        python3-matplotlib \
        python3-tqdm \
        python3-click \
        python3-xmodem \
        python3-paho-mqtt \
        python3-serial \
        python3-yaml \
        python3-defusedxml \
        && \
    apt-get clean

RUN set -ex && \
    python3 -m pip install --no-cache-dir --no-deps --break-system-packages supervision && \
    python3 -m pip install --no-deps --break-system-packages -e /home/python-sscma && \
    rm -fr /tmp/*

ENTRYPOINT ["sscma.cli"]
