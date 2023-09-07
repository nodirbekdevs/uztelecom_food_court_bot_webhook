FROM python:3.11.0-alpine as builder

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED=1

RUN apk add --no-cache build-base
RUN mkdir /install
WORKDIR /install

COPY ./requirements.txt /install/requirements.txt
RUN pip install --prefix=/install -r /install/requirements.txt

#COPY /pyproject.toml /install/pyproject.toml
#RUN pip3 install poetry
#RUN poetry config virtualenvs.create false
#RUN poetry install --no-root

FROM python:3.11.0-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED=1

RUN mkdir /code

WORKDIR /code

COPY --from=builder /install /usr/local
COPY . /code/

EXPOSE 8250