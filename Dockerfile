FROM --platform=$TARGETPLATFORM python:3-slim-bookworm as builder

WORKDIR /tmp

COPY . /tmp

RUN set -ex && \
    python3 -m pip install build && \
    python3 -m build --sdist && \
    tar -xzf dist/*.tar.gz -C dist && \
    rm dist/*.tar.gz


FROM --platform=$TARGETPLATFORM python:3-slim-bookworm

WORKDIR /tmp


COPY --from=builder /tmp/requirements.txt /tmp/
COPY --from=builder /tmp/dist/python-sscma-* /home/python-sscma

RUN set -ex && \
     python3 -m pip install --no-cache-dir -r /tmp/requirements.txt && \
     python3 -m pip install --no-deps -e /home/python-sscma && \
     rm -fr /tmp/*

ENTRYPOINT ["sscma.cli"]
