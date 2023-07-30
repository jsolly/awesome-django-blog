FROM python:3.8.17-alpine3.18
LABEL maintainer="jsolly"

# Make sure Python output is sent straight to terminal
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
COPY ./django_project /app

WORKDIR /app
EXPOSE 8000

RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r /requirements.txt && \
    adduser -disabled-password --no-create-home app && \

ENV PATH="/py/bin:$PATH"

USER app
