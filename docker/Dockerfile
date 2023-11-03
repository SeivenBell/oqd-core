FROM python:3.10.13-slim-bookworm

WORKDIR /app

ADD . /app

ENV PYTHONPATH /app

RUN pip install .

CMD rq worker --with-scheduler & python main.py
