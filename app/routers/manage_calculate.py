from fastapi import APIRouter
from app.config.settings import get_settings
from app.workers.tasks import calculate_scheduler_task
from app.helpers.connector_pgsql import PostgresConnector
from app.main_celery import app_celery
from app.handlers.calculate.schemas import RequestCalculate


manage_calculate_routers = APIRouter()
settings = get_settings()

connector = PostgresConnector(
    host=settings.db_host,
    user=settings.db_user,
    password=settings.db_password,
    dbname=settings.db_name_database,
    port=settings.db_port
)


@manage_calculate_routers.post("/task/run")
async def run_calculate(request: RequestCalculate):
    """
    Запуска задачи на расчет маршрутов ледоколов
    :param request:
    :return:
    """
    params = request.params
    task = calculate_scheduler_task.delay(params)
    return {"task_id": str(task.id)}


@manage_calculate_routers.get("/task/{task_id}")
async def get_task_status(task_id: str):
    """
    Получение статуса задачи по task_id
    :param task_id:
    :return:
    """
    task = app_celery.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": task.status,
        "result": task.result if task.successful() else None
    }
