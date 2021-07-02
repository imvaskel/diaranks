FROM python:3.9.5-slim-buster
LABEL maintainer="vaskel <contact@vaskel.xyz>"
RUN apt update && apt-get install gcc git -y && pip install --upgrade pip setuptools wheel
WORKDIR /src/
COPY requirements.txt ./
RUN pip install -r requirements.txt --ignore-installed
COPY . .
RUN chmod +x wait-for-it.sh
CMD ["python", "bot.py"]