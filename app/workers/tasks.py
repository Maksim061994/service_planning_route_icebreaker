from app.main_celery import app_celery
from app.workers.calculate_scheduler import CalculateScheduler
from app.workers.add_order import AddOrder
from app.config.settings import get_settings


settings = get_settings()


@app_celery.task
def calculate_scheduler_task(params):
    calculate = CalculateScheduler(settings=settings)
    best_try_reward = calculate.compute_schedule(params)
    calculate.save_results()
    calculate.save_dataframe()
    return -best_try_reward


@app_celery.task
def add_order_to_table_task(order_id: int):
    process = AddOrder(settings=settings)
    all_time = process.add_new_order_to_db(order_id)
    return all_time

@app_celery.task
def add_icebreaker_to_table_task(icebreaker_id: int):
    process = AddOrder(settings=settings)
    all_time = process.add_new_icebreaker_to_db(icebreaker_id)
    return all_time
