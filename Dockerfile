
FROM debian:stable-slim

WORKDIR /tmp

COPY dist /tmp/dist
COPY requirements.txt /tmp/requirements.txt

RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    apt-get install -y ffmpeg libsm6 libxext6 && \
    python3 -m pip install --no-cache-dir --break-system-packages -r /tmp/requirements.txt && \
    python3 -m pip install --no-cache-dir --break-system-packages /tmp/dist/*.whl

ENTRYPOINT ["sscma.cli"]
