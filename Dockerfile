FROM ubuntu:latest
MAINTAINER Team Lakshya


RUN apt update && apt install -y python3-pip libmysqlclient-dev

COPY . /app

WORKDIR /app

RUN pip3 install -r requirements.txt

CMD [python3","manage.py","runserver"]
