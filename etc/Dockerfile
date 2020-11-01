FROM ubuntu:20.04

LABEL maintainer="gallegoj@uw.edu"

WORKDIR /opt

# Need to install libusb
RUN apt-get -y update
RUN apt-get -y install libusb-1.0-0 python3 python3-pip

# This Dockerfile is mean to be run with context the root of flicamera
COPY . flicamera

RUN rm -f flicamera/libfli*.so
RUN cd flicamera && pip3 install .

# This is the default port but the real port is exposed
# when starting the service.
EXPOSE 19995

# Default actor name. Can be overriden when running the container.
ENV ACTOR_NAME=flicamera

ENTRYPOINT flicamera actor --host 0.0.0.0 \
           --actor-name $ACTOR_NAME start --debug
