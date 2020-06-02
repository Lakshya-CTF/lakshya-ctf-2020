FROM ubuntu:latest
MAINTAINER Team Lakshya


RUN apt update && apt install -y python3-pip libmysqlclient-dev mysql-client

COPY . /app

WORKDIR /app

RUN pip3 install -r requirements.txt

CMD ["python3","manage.py","runserver","0.0.0.0:8000"]
