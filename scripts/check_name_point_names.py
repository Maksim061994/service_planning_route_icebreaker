import pandas as pd
from tqdm import tqdm
from typing import Tuple

from app.helpers.connector_pgsql import PostgresConnector


async def main():
    conn = PostgresConnector(
        host="localhost", user="test", password="test",
        dbname="ship_tracking", port=5432
    )
    conn.connect()
    orders = await conn.get_data_async("select * from orders")
    points = await conn.get_data_async("select * from points")
    conn.close()

    points_name = [p['point_name'] for p in points]

    for order in tqdm(orders):
        point_start = order['point_start']
        point_end = order['point_end']
        if point_start not in points_name:
            print(f"Point {point_start} not found")
        if point_end not in points_name:
            print(f"Point {point_end} not found")


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
