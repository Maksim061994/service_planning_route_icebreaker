import logging

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.logger import logger as fastapi_logger

# custom libs
from app.routers.user_access import user_access_router
from app.routers.nsi import nsi_routers
from app.routers.manage_orders import manage_orders_routers
from app.routers.manage_icebreakers import manage_icebreakers_routers
from app.routers.manage_calculate import manage_calculate_routers

from app.helpers.verify_token import verify_token



# setup logger
gunicorn_error_logger = logging.getLogger("gunicorn.error")
gunicorn_logger = logging.getLogger("gunicorn")
uvicorn_access_logger = logging.getLogger("uvicorn.access")
uvicorn_access_logger.handlers = gunicorn_error_logger.handlers
fastapi_logger.handlers = gunicorn_error_logger.handlers


app = FastAPI(
    title="API доступа к управлению расчетами",
    description="Сделано в рамках хакатона",
    version="0.0.1",
    contact={
        "name": "Maksim Kulagin",
        "email": "maksimkulagin06@yandex.ru",
    }
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['POST', 'GET'],
    allow_headers=['*'],
    allow_credentials=True,
)

# users
app.include_router(
    user_access_router, prefix='/users',
    tags=['user_access_router']
)

app.include_router(
    nsi_routers, prefix='/nsi',
    tags=['nsi_routers'],
    dependencies=[Depends(verify_token)]
)

app.include_router(
    manage_orders_routers, prefix='/orders',
    tags=['manage_orders_routers'],
    dependencies=[Depends(verify_token)]
)

app.include_router(
    manage_icebreakers_routers, prefix='/icebreakers',
    tags=['manage_icebreakers_routers'],
    dependencies=[Depends(verify_token)]
)

app.include_router(
    manage_calculate_routers, prefix='/calculate',
    tags=['manage_calculate_routers'],
    dependencies=[Depends(verify_token)]
)
