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

COPY etc/entrypoint.sh .
RUN ["chmod", "+x", "entrypoint.sh"]

ENTRYPOINT ["./entrypoint.sh"]
