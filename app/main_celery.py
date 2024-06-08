from celery import Celery
from app.config.settings import get_settings

settings = get_settings()

celery = Celery(
    __name__,
    broker=settings.celery_broker_url,
    backend=settings.celery_backend_url
)

celery.conf.update(
    CELERY_IMPORTS=("app.workers.tasks",)
)

if __name__ == "__main__":
    celery.start()
