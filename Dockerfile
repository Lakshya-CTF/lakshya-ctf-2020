FROM ubuntu:latest
MAINTAINER Team Lakshya

RUN apt update && apt install -y python3-pip libmysqlclient-dev mysql-client

COPY . /app

WORKDIR /app

RUN pip3 install -r requirements.txt

RUN python3 manage.py createcachetable

RUN python3 manage.py makemigrations

RUN python3 manage.py migrate 

CMD ["gunicorn","CTFFinal.wsgi","--workers","5","--bind","0.0.0.0:8000"]
