FROM python:3.8-buster

MAINTAINER Ralf Junghanns <ralf.junghanns@gmail.com>

RUN buildDeps="unzip wget g++ gfortran make" && \
    apt-get update && \
    apt-get install -y $buildDeps --no-install-recommends && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install the requirements
COPY ./app /app
RUN pip install -r /app/requirements.txt

# Compile modflow-excecutables
RUN pip install https://github.com/inowas/pymake/archive/1.1.zip
COPY ./docker/pyMake-scripts /scripts
WORKDIR /scripts
RUN for file in ./*; do python $file 2>/dev/null; done
RUN mv ./temp/* /usr/local/bin
RUN rm -rf /pymake-1.1

WORKDIR /app
