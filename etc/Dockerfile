FROM python:3.8.6-alpine3.12

LABEL maintainer="gallegoj@uw.edu"

WORKDIR /opt

# This Dockerfile is mean to be run with context the root of flicamera
COPY . flicamera
RUN cd flicamera && pip install .

ENTRYPOINT flicamera
