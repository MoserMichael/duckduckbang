FROM alpine:3.12 

ARG GITHUB_TOKEN=""

RUN apk add bash python3 git expect py3-pip g++ libc-dev python3-dev
RUN pip3 install html5lib
RUN pip3 install Brotli

WORKDIR /

COPY build_cats.py /
COPY comm.py /
COPY getselen.py /
COPY gettitle.py /
COPY build/build-in-docker.sh /
COPY description_cache.json / 
COPY build/ex /

RUN GITHUB_TOKEN=${GITHUB_TOKEN} ./build-in-docker.sh





