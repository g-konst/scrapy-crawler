FROM python:3.12-slim

WORKDIR /app

COPY dist/*.whl .
COPY scrapy.cfg .

RUN pip install *.whl
