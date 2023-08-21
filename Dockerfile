FROM python:3.11-alpine
LABEL maintainer="jsolly"

# Make sure Python output is sent straight to terminal
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
COPY ./app /app

WORKDIR /app
EXPOSE 8000

RUN apk add --no-cache gcc g++ musl-dev python3-dev linux-headers openblas-dev make freetype-dev && \
    python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r /requirements.txt && \
    adduser --disabled-password --home /dev/null app && \
    mkdir -p /fontconfig_cache && \
    chown -R app:app /fontconfig_cache

ENV PATH="/py/bin:$PATH"

USER app
