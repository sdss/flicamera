FROM ubuntu:20.04

LABEL maintainer="gallegoj@uw.edu"

WORKDIR /opt

# Need to install libusb
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get -y update
RUN apt-get -y install libusb-1.0-0 libusb-1.0-0-dev python3 python3-pip git gzip

COPY . flicamera

RUN rm -f flicamera/libfli*.so
RUN pip3 install -U pip wheel setuptools
RUN cd flicamera && pip3 install .

# This is the default port but the real port can be changed when
# starting the service.
EXPOSE 19995

# Default actor name. Can be overriden when running the container.
ENV ACTOR_NAME=flicamera
ENV PYTHONPATH=/home/sdss5/software/actorkeys/sdss5/python

# Connect repo to package
LABEL org.opencontainers.image.source https://github.com/sdss/flicamera

# Need to use --host 0.0.0.0 because the container won't listen to 127.0.0.1
# See https://bit.ly/2HUwEms
# Also, set umask to 775 to create new directories and files with
# group write permissions.
ENTRYPOINT umask ug=rwx,o=rx && flicamera actor --host 0.0.0.0 \
           --actor-name $ACTOR_NAME start --debug
