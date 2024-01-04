#!/bin/bash

rm -rf dist

python3 setup.py bdist_wheel

docker build . -t python-sscma:latest
