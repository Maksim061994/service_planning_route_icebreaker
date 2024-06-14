#!/bin/sh -ex
gunicorn app.main:app -k uvicorn.workers.UvicornWorker &
celery -A app.main_celery.app_celery beat -l debug &
celery -A app.main_celery.app_celery worker -E --pool=prefork -O fair -c 4 -l INFO &
celery -A app.main_celery.app_celery flower &

tail -f /dev/null
