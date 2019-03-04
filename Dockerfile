FROM ubuntu:latest

# Update base container install
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential

# Set python aliases for python3
RUN echo 'alias python=python3' >> ~/.bashrc
RUN echo 'alias pip=pip3' >> ~/.bashrc

COPY ./requirements.txt /requirements.txt
WORKDIR /app

# Before installing GDAL we need to install the requirements
RUN pip install -r /requirements.txt

CMD ["python", "app.py"]