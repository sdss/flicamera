FROM ubuntu:20.04

LABEL maintainer="gallegoj@uw.edu"

WORKDIR /opt

# Need to install libusb
RUN apt-get -y update
RUN apt-get -y install libusb-1.0-0 libusb-1.0-0-dev python3 python3-pip

# Uncomment this and comment COPY below to use a local version of basecam.
# Run from the root of flicamera with docker build -f Dockerfile ..
# COPY ./flicamera flicamera

# Normal mode
COPY . flicamera

RUN rm -f flicamera/libfli*.so
RUN pip3 install -U pip wheel setuptools
RUN cd flicamera && pip3 install .

# Uncomment this to use a local version of basecam.
# RUN cd ..
# COPY ./basecam basecam
# RUN pip3 uninstall -y sdss-basecam
# RUN cd basecam && pip3 install -U .

# This is the default port but the real port can be changed when
# starting the service.
EXPOSE 19995

# Default actor name. Can be overriden when running the container.
ENV ACTOR_NAME=flicamera

# Connect repo to package
LABEL org.opencontainers.image.source https://github.com/sdss/flicamera

# Need to use --host 0.0.0.0 because the container won't listen to 127.0.0.1
# See https://bit.ly/2HUwEms
# Also, set umask to 775 to create new directories and files with
# group write permissions.
ENTRYPOINT umask ug=rwx,o=rx && flicamera actor --host 0.0.0.0 \
           --actor-name $ACTOR_NAME start --debug
