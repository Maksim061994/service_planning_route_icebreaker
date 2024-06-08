from app.main_celery import celery
from app.workers.calculate_scheduler import CalculateScheduler


@celery.task
def calculate_scheduler_task(x, y):
    calculate = CalculateScheduler()
    result = calculate.divide(x, y)
    return result
