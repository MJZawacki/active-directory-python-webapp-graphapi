#FROM python:3.6.1
FROM tiangolo/uwsgi-nginx-flask:python3.6-alpine3.7

# Set the working directory to /app

# Copy the current directory contents into the container at /app 

# Install the dependencies
RUN apk add build-base
RUN apk add openssl-dev libffi-dev
RUN pip install --no-cache-dir -U pip

WORKDIR /flaskapp
ENV UWSGI_INI uwsgi.ini
ENV LISTEN_PORT=5000
ENV ENVIRONMENT=dev
EXPOSE 5000 
ADD . /flaskapp
RUN pip install --no-cache-dir -r ./requirements.txt
