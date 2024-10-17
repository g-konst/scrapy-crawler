FROM python:3.12-slim

WORKDIR /app

COPY dist/*.whl .

RUN pip install *.whl
