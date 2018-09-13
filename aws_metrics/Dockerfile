FROM python:alpine

EXPOSE 5000

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY src /app
WORKDIR /app
ENTRYPOINT FLASK_APP=app.py flask run
