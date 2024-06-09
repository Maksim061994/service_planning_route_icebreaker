from fastapi import APIRouter

# handlers
from app.config.settings import get_settings
from app.handlers.nsi.base import Nsi
from app.helpers.connector_pgsql import PostgresConnector


nsi_routers = APIRouter()
settings = get_settings()

connector = PostgresConnector(
    host=settings.db_host,
    user=settings.db_user,
    password=settings.db_password,
    dbname=settings.db_name_database,
    port=settings.db_port
)


@nsi_routers.get('/edges')
async def edges():
    """
    Получение списка всех ребер графа (взаимосвязей между портами
    :return:
    """
    nsi = Nsi(settings, connector)
    return await nsi.get_edges()


@nsi_routers.get('/points')
async def points():
    """
    Получение списка всех точек графа (портов)
    :return:
    """
    nsi = Nsi(settings, connector)
    return await nsi.get_points()
