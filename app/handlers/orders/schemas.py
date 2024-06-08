from pydantic import BaseModel, validator
from datetime import datetime


class RequestOrder(BaseModel):
    name_ship: str
    class_ship: str
    point_start: str
    point_end: str
    speed: float
    date_start_swim: str

    @validator('date_start_swim')
    def validate_date(cls, v):
        try:
            return datetime.strptime(v, '%Y-%m-%d')  # specify your date format here
        except ValueError:
            raise ValueError('Invalid date format. Expected YYYY-MM-DD')


class RequestDeleteOrder(BaseModel):
    order_id: int
