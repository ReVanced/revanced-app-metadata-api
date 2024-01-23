FROM python:3.11-slim

ARG SEARCH_API_KEY
ARG SEARCH_ENGINE_ID
ARG REDIS_URL

ENV SEARCH_API_KEY $SEARCH_API_KEY
ENV SEARCH_ENGINE_ID $SEARCH_ENGINE_ID
ENV REDIS_URL $REDIS_URL

WORKDIR /usr/src/app

COPY . .

RUN apt update && \
    apt-get install git build-essential libffi-dev libssl-dev openssl --no-install-recommends -y \
    && pip install --no-cache-dir -r requirements.txt

CMD [ "python3", "run.py"]
