# pull official base image
FROM python:3.10

# set work directoryapk update \
                    #    && apk add postgresql-dev gcc python3-dev musl-dev
#RUN mkdir /usr/src/app
#RUN mkdir /usr/src/app/static
#RUN mkdir /usr/src/app/media
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apt-get update  \
    && apt-get install netcat -y  \
    && apt-get install -y postgresql-server-dev-all gcc python3-dev musl-dev

# install dependencies
RUN pip install --upgrade pip

COPY ./requirements.txt .
RUN pip install -r requirements.txt


COPY ./docker-entrypoint.sh .

RUN ["chmod", "+x", "/usr/src/app/docker-entrypoint.sh"]

# copy project
COPY . .



# run entrypoint.sh
ENTRYPOINT ["/usr/src/app/docker-entrypoint.sh"]