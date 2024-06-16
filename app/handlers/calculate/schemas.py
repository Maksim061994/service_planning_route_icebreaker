from pydantic import BaseModel


class RequestCalculate(BaseModel):
    params: dict
