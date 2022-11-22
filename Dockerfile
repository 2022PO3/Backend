FROM  python:3.10.7-slim-bullseye 

WORKDIR /backend
ENV PYTHONUNBUFFERED=1
COPY requirements.txt requirements.txt
COPY ./docker/run.sh /docker/run.sh
COPY ./docker/seeds.sh /docker/seeds.sh
COPY ./google_vision_api_credentials.json ./google_vision_api_credentials.jso
RUN chmod +x /docker/run.sh

# Install the MySQL-client for Python and the gcc compiler for C++.
RUN apt-get update && apt-get install -y libmariadb-dev build-essential netcat libpq-dev

# Update pip
RUN pip3 install --upgrade pip
# Install all the dependencies of the project.
RUN pip3 install -r requirements.txt
RUN pip3 install opencv-python==4.5.5.64
RUN pip3 install psycopg2
RUN pip3 install faker

ENTRYPOINT ["/docker/run.sh"]
