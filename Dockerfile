FROM ubuntu:18.04
MAINTAINER "DIBBS"

RUN \
  apt-get update && \
  apt-get -y upgrade && \
  apt-get install -y python3 python3-pip python-dev wget unzip

RUN pip3 install twisted
RUN pip3 install datetime
RUN pip3 install requests

ADD phishmonger_code.zip /
RUN unzip phishmonger_code.zip

WORKDIR "/phishmonger"

# CMD [ "python3", "./pullPhishLoop.py" ]
