from fastapi import APIRouter
from app.config.settings import get_settings
from app.workers.tasks import calculate_scheduler_task
from app.helpers.connector_pgsql import PostgresConnector
from app.main_celery import celery
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
    task = calculate_scheduler_task.delay(request.x, request.y)
    return {"task_id": str(task.id)}


@manage_calculate_routers.get("/task/{task_id}")
async def get_task_status(task_id: str):
    task = celery.AsyncResult(task_id)
    return {"task_id": task_id, "status": task.status, "result": task.result if task.successful() else None}
