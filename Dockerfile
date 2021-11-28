FROM python:3.9
LABEL maintainer="vaskel <contact@vaskel.xyz>"
RUN apt-get update \
    && apt-get install gcc git -y \
    && pip install --upgrade pip setuptools wheel poetry
WORKDIR /src/
COPY poetry.lock pyproject.toml /src/
COPY . .
RUN poetry install \
    && chmod +x wait-for-it.sh
CMD ["poetry", "run", "python", "bot.py"]