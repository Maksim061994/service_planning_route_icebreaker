from celery import Celery
from app.config.settings import get_settings

settings = get_settings()

app_celery = Celery(
    __name__,
    broker=settings.celery_broker_url,
    backend=settings.celery_backend_url
)
app_celery.conf.update(
    imports=("app.workers.tasks",),
    task_track_started=True,
    result_persistent=True
)

if __name__ == "__main__":
    app_celery.start()
