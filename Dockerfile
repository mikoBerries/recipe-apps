FROM python:3.9-alpine3.13
LABEL maintainer="miko.com"

ENV PYTHONUNBUFFERED 1

# copy depedency file
COPY ./requirement.txt /tmp/requirement.txt
COPY ./requirement.dev.txt /tmp/requirement.dev.txt

# copy source code
COPY ./app /app

WORKDIR /app
EXPOSE 8000

ARG DEV=false

# create virtual env 
# upgrading pip
# installing psycopg2 depedency for alpine images
# instaling depedency for python project
# add user for alpine images to log instead root user
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client jpeg-dev && \
    apk add --update --no-cache --virtual .tmp-build-deps \
    build-base postgresql-dev musl-dev zlib zlib-dev && \
    /py/bin/pip install -r /tmp/requirement.txt && \
    if [ $DEV="true" ]; \
    then /py/bin/pip install -r /tmp/requirement.dev.txt ; \
    fi && \
    rm -rf /tmp && \
    # apk del .tmp-build-deps && \
    adduser\
    --disabled-password \
    --no-create-home \
    django-user

# update global env
ENV PATH="/py/bin:$PATH"

# log using selected user (created user)
USER django-user