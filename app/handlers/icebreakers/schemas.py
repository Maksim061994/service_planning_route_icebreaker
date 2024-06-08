from pydantic import BaseModel


class RequestIcebreaker(BaseModel):
    name_icebreaker: str
    speed: float
    class_icebreaker: str
    start_position: str

class RequestDeleteIcebreaker(BaseModel):
    icebreaker_id: int
