#!/bin/sh -ex
gunicorn app.main:app -k uvicorn.workers.UvicornWorker &
celery -A app.celery.celery.celery_app beat -l debug &
celery -A app.celery.celery.celery_app worker -E --pool=prefork -O fair -c 4 -l INFO &
celery -A app.celery.celery.celery_app flower &

tail -f /dev/null
