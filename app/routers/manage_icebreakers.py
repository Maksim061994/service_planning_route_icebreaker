from fastapi import APIRouter
from app.config.settings import get_settings
from app.handlers.icebreakers.manager import ManagerIcebreakers
from app.handlers.icebreakers.schemas import RequestIcebreaker, RequestDeleteIcebreaker
from app.helpers.connector_pgsql import PostgresConnector


manage_icebreakers_routers = APIRouter()
settings = get_settings()

connector = PostgresConnector(
    host=settings.db_host,
    user=settings.db_user,
    password=settings.db_password,
    dbname=settings.db_name_database,
    port=settings.db_port
)


@manage_icebreakers_routers.get('/')
async def get_list_Icebreakers():
    manager = ManagerIcebreakers(settings, connector)
    return await manager.get_icebreakers()

@manage_icebreakers_routers.post('/add')
async def create_Icebreaker(request: RequestIcebreaker):
    manager = ManagerIcebreakers(settings, connector)
    return await manager.create_icebreaker(request)

@manage_icebreakers_routers.post('/delete')
async def delete_Icebreaker(request: RequestDeleteIcebreaker):
    manager = ManagerIcebreakers(settings, connector)
    return await manager.delete_icebreaker(order_id=request.icebreaker_id)
