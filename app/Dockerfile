FROM python:3.7.2-stretch

COPY . /app

WORKDIR /app

# Install the requirements
RUN pip install numpy
RUN pip install -r ./requirements.txt

CMD ["python", "app.py"]