FROM alpine:3.12 

ARG GITHUB_TOKEN=""

RUN apk add bash python3 git expect

WORKDIR /

COPY build-cats.py /
COPY build/build-in-docker.sh /
COPY build/ex /

RUN GITHUB_TOKEN=${GITHUB_TOKEN} ./build-in-docker.sh





