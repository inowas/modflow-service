FROM python:3.8-buster

MAINTAINER Ralf Junghanns <ralf.junghanns@gmail.com>

RUN buildDeps="unzip wget g++ gfortran make" && \
    apt-get update && \
    apt-get install -y $buildDeps --no-install-recommends && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


COPY . /app
WORKDIR /app

# Install the requirements
RUN pip install -r ./requirements.txt

# Compile modflow-excecutables
RUN pip install https://github.com/modflowpy/pymake/archive/1.1.zip

COPY pyMake-scripts /scripts

RUN pip install requests

WORKDIR /scripts
RUN for file in ./*; do python $file 2>/dev/null; done
RUN mv ./temp/* /usr/local/bin

WORKDIR /app

RUN rm -rf /pymake-1.1
