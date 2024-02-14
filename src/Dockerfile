FROM python:3.10 AS AUTH

WORKDIR /app

COPY requirements.txt requirements.txt

COPY entrypoint.sh entrypoint.sh

RUN  pip install --upgrade pip --no-cache-dir && pip install -r requirements.txt --no-cache-dir

RUN apt-get update && apt-get install -y netcat-traditional

COPY . .

EXPOSE 8000

RUN chmod +x ./entrypoint.sh

ENTRYPOINT ["/bin/bash", "./entrypoint.sh"]