FROM python:3.12-slim AS builder

RUN apt update && \
    apt-get install git build-essential libffi-dev libssl-dev openssl --no-install-recommends -y &&\
    pip install --no-cache-dir poetry

ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN --mount=type=cache,target=$POETRY_CACHE_DIR \
    poetry install --no-interaction --without dev --no-root

FROM python:3.12-slim AS runner

ARG USERNAME=dockeruser
ARG UID=124
ARG GID=$UID
ARG SEARCH_API_KEY
ARG SEARCH_ENGINE_ID
ARG REDIS_URL

ENV SEARCH_API_KEY=$SEARCH_API_KEY
ENV SEARCH_ENGINE_ID=$SEARCH_ENGINE_ID
ENV REDIS_URL=$REDIS_URL

RUN rm -rf /var/lib/apt/lists/* && \
    groupadd --gid $GID $USERNAME && \
    useradd --uid $UID --gid $GID --no-create-home $USERNAME && \
    mkdir -p /app && \
    chown -R $USERNAME:$USERNAME /app

ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY --from=builder --chown=${GID}:${UID} ${VIRTUAL_ENV} ${VIRTUAL_ENV}

WORKDIR /app

COPY --chown=${GID}:${UID} . .

USER ${GID}:${UID}

CMD ["python", "run.py"]
