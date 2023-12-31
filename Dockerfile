FROM registry.nextpertise.tools/nextpertise/uvicorn-fastapi-poetry:python3.11
ENV APP_MODULE="main:app"

# Copy using poetry.lock* in case it doesn't exist yet
COPY ./pyproject.toml ./poetry.lock* /app/

RUN poetry install --no-root --only main

COPY src/ /app/
