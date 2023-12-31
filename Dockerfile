# syntax=docker/dockerfile:1

ARG APP_NAME=reverse_words_v1.1
ARG TESTED_APIS_LIST=reverse,restore

FROM python:3

WORKDIR /usr/src/app

COPY src/ .
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "app.py" ]

EXPOSE 5000