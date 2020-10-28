FROM inowas/modflow-build:latest

MAINTAINER Ralf Junghanns <ralf.junghanns@gmail.com>

# Install the requirements
COPY ./app /app
WORKDIR /app
RUN pip install -r ./requirements.txt
