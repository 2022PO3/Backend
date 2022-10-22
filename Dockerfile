FROM  python:3.10.7-slim-bullseye 

WORKDIR /backend
ENV PYTHONUNBUFFERED=1
COPY requirements.txt requirements.txt
COPY requirements-dev.txt requirements-dev.txt
COPY ./docker/run.sh /docker/run.sh
RUN chmod +x /docker/run.sh

# Install the MySQL-client for Python and the gcc compiler for C++.
RUN apt-get update && apt-get install -y libmariadb-dev build-essential netcat libpq-dev

# Install all the dependencies of the project.
RUN pip3 install -r requirements.txt
RUN pip3 install psycopg2

ENTRYPOINT ["/docker/run.sh"]
