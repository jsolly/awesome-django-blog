FROM python:3.11-slim-buster
LABEL maintainer="jsolly"

# Make sure Python output is sent straight to terminal
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
COPY ./app /app

WORKDIR /app
EXPOSE 8000

RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r /requirements.txt && \
    adduser --disabled-password --gecos '' --no-create-home app && \
    mkdir -p /fontconfig_cache && \
    chown -R app:app /fontconfig_cache && \
    mkdir -p /vol/web/static && \
    mkdir -p /vol/web/media && \
    chown -R app:app /vol && \
    chmod -R 755 /vol

ENV PATH="/py/bin:$PATH"

USER app
