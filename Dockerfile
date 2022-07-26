FROM ubuntu:22.04 as base
RUN apt-get update
RUN apt-get upgrade -y
RUN DEBIAN_FRONTEND=noninteractive apt install wget vim -y
WORKDIR /sd22
COPY . ./
RUN ./docker_setup.sh
