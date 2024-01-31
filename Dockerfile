
FROM --platform=$TARGETPLATFORM python:3-slim-bookworm as builder

WORKDIR /tmp

COPY . /tmp

RUN set -ex && \
    python3 setup.py bdist_wheel


FROM --platform=$TARGETPLATFORM python:3-slim-bookworm

WORKDIR /tmp

COPY --from=builder /tmp/dist/*.whl /tmp/dist/
COPY --from=builder /tmp/requirements.txt /tmp/

RUN set -ex && \
    python3 -m pip install -r /tmp/requirements.txt && \
    python3 -m pip install --no-cache-dir /tmp/dist/*.whl && \
    rm -fr /tmp/*

ENTRYPOINT ["sscma.cli"]
