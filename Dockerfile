FROM python:3.7.2-stretch

COPY ./requirements.txt /requirements.txt
WORKDIR /app

# Before installing GDAL we need to install the requirements
RUN pip install -r /requirements.txt

CMD ["python", "app.py"]