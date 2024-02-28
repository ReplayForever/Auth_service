#!/bin/bash

while ! nc -z redis 6379; do
    sleep 1
done

while ! nc -z auth_postgres 5434; do
    sleep 1
done

alembic upgrade head

gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8002
