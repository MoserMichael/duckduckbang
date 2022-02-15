FROM alpine:3.12 

ARG GITHUB_TOKEN=""

RUN apk add bash python3 git expect py3-pip g++ libc-dev python3-dev linux-headers
RUN pip3 install html5lib
RUN pip3 install Brotli
RUN pip3 install psutil

WORKDIR /

COPY build_cats.py /
ADD  scrapscrap /
COPY scrapscrap /scrapscrap
COPY build/build-in-docker.sh /
COPY description_cache.json / 
COPY build/ex /

RUN GITHUB_TOKEN=${GITHUB_TOKEN} ./build-in-docker.sh





