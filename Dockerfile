FROM python:alpine

WORKDIR /app

COPY . /app

COPY ./requirements.txt  /app

RUN pip3 install --upgrade pip

RUN pip3 install -r requirements.txt

EXPOSE 5000


