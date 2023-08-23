FROM registry.nextpertise.tools/nextpertise/python-poetry:3.11

# Copy using poetry.lock* in case it doesn't exist yet
COPY ./pyproject.toml ./poetry.lock* /app/

RUN poetry install --no-root --no-dev

COPY src/ /app/

ENTRYPOINT ["/app/main.py"]