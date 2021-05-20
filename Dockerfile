FROM python:3.8-slim-buster

LABEL maintainer="Tyler Cinkant <tcinkant@gmail.com>"


COPY ./app/requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install -r requirements.txt

COPY ./app /app

CMD [ "python3", "-u", "./app.py" ]
