FROM python:3.8-buster

COPY . /app

WORKDIR /app

# Install the requirements
RUN pip install -r ./requirements.txt

CMD ["python", "app.py"]