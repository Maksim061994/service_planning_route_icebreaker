from pydantic import BaseModel


class RequestCalculate(BaseModel):
    x: int
    y: int
