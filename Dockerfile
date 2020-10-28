FROM python:3.8-buster

MAINTAINER Ralf Junghanns <ralf.junghanns@gmail.com>

COPY --from=inowas/modflow-build:latest /modflow-bin/. /usr/local/bin/

# Install the requirements
COPY ./app /app
WORKDIR /app
RUN pip install -r ./requirements.txt
