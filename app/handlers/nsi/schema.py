from pydantic import BaseModel


class PointsResponseSchema(BaseModel):
    id: int
    latitude: float
    longitude: float
    point_name: str
