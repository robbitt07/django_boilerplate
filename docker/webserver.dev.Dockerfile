# As Django/Carrot runs on Python, I choose the official Python 3 Docker image.
FROM python:3.8.3

RUN apt-get update -qq && apt-get install -y -qq \
    # std libs
    git less nano curl \
    ca-certificates \
    wget build-essential\
    # postgresql
    libpq-dev postgresql-client && \
    apt-get clean all && rm -rf /var/apt/lists/* && rm -rf /var/cache/apt/*

# Set the working directory to /usr/src/app.
WORKDIR /usr/src/app

# Copy the file from the local host to the filesystem of the container at the working directory.
COPY requirements.txt ./

# Install Scrapy specified in scrapy-requirements.txt.
RUN pip3 install --no-cache-dir --no-use-pep517 -r requirements.txt

# Copy the project source code from the local host to the filesystem of the container at the working directory.
COPY . .

# Run the Web Server when the container launches.
RUN python manage.py collectstatic --noinput

# Run the Web Server when the container launches.
CMD exec \
    gunicorn \
    <django_package_name>.wsgi:application \
    --log-config /usr/src/app/logging.dev.conf \
    --bind 0.0.0.0:8000 \
    --timeout 180 \
    --log-level info \
    --workers 2