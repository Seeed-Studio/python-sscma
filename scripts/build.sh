#!/bin/bash

docker buildx use default && \
docker buildx build --platform linux/arm64 -t python-sscma . --load && \
mkdir -p release && \
docker save python-sscma > "release/python-sscma-$(date +%Y-%m-%d)-$(date +%s).tar"
