from pydantic_settings import BaseSettings
from pydantic import Extra
import os


ENV_API = os.getenv("ENVIRONMENT")


class Settings(BaseSettings):
    # user
    secret_key: str
    algorithm: str
    access_token_expires_hours: int

    # db
    db_host: str
    db_port: int
    db_user: str
    db_password: str
    db_name_database: str = "ship_tracking"
    db_name_table_edges: str = "edges"
    db_name_table_orders: str = "orders"
    db_name_table_points: str = "points"
    db_name_table_route_orders: str = "route_orders"
    db_name_table_icebreakers: str = "icebreakers"
    db_name_table_route_icebreakers: str = "route_icebreakers"

    # celery
    celery_broker_url: str
    celery_backend_url: str

    class Config:
        env_file = ".env" if not ENV_API else f".env.{ENV_API}"
        extra = Extra.ignore


def get_settings():
    return Settings()
