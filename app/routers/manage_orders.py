from fastapi import APIRouter
from app.config.settings import get_settings
from app.handlers.orders.manager import ManagerOrders
from app.handlers.orders.schemas import RequestOrder, RequestDeleteOrder
from app.helpers.connector_pgsql import PostgresConnector


manage_orders_routers = APIRouter()
settings = get_settings()

connector = PostgresConnector(
    host=settings.db_host,
    user=settings.db_user,
    password=settings.db_password,
    dbname=settings.db_name_database,
    port=settings.db_port
)


@manage_orders_routers.get('/')
async def get_list_orders(start=None, end=None):
    """
    Получение списка всех заявок на перевозку судов
    :param start:
    :param end:
    :return:
    """
    manager = ManagerOrders(settings, connector)
    return await manager.get_orders(date_start=start, date_end=end)

@manage_orders_routers.post('/add')
async def create_order(request: RequestOrder):
    """
    Добавление новой заявки на перевозку судов
    :param request:
    :return:
    """
    manager = ManagerOrders(settings, connector)
    return await manager.create_order(request)

@manage_orders_routers.post('/delete')
async def delete_order(request: RequestDeleteOrder):
    """
    Удаление заявки на перевозку судов
    :param request:
    :return:
    """
    manager = ManagerOrders(settings, connector)
    return await manager.delete_order(order_id=request.order_id)
