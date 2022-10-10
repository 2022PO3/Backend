FROM  python:3.10.7-slim-bullseye

WORKDIR /backend
ENV PYTHONUNBUFFERED=1
COPY requirements.txt requirements.txt

# Install the MySQL-client for Python and the gcc compiler for C++.
RUN apt-get update && apt-get install -y libmariadb-dev build-essential

# Install all the dependencies of the project.
RUN pip3 install -r requirements.txt
