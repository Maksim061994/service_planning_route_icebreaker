import pickle
import pandas as pd
from app.helpers.connector_pgsql import PostgresConnector


async def main():
    with open('data/clean_orders.pickle', 'rb') as f:
        clean_orders = pickle.load(f)
    conn = PostgresConnector(
        host="localhost", user="test", password="test",
        dbname="ship_tracking", port=5432
    )
    conn.connect()
    parameter = await conn.get_data_async("select * from parameters where name='date_start'")
    orders = await conn.get_data_async("select * from orders")
    points = await conn.get_data_async("select * from points")
    d_orders = {orders[i]["id"]: (orders[i]["point_start"], orders[i]["point_end"]) for i in range(len(orders))}
    d_points = {points[i]["point_name"]: points[i]["id"] for i in range(len(points))}
    date_start = pd.to_datetime(parameter[0]['value'])

    for k, type_route in clean_orders:
        point_start_id_icebreaker = k[0]
        point_end_id_icebreaker = k[1]
        date = (date_start + pd.Timedelta(hours=k[2])).strftime("%Y-%m-%d")
        order_id = k[3]
        point_start_id = d_points[d_orders[order_id][0]]
        point_end_id = d_points[d_orders[order_id][1]]
        query = f"""
            INSERT INTO route_orders (order_id, point_start_id, point_end_id, point_start_id_icebreaker, point_end_id_icebreaker, date_start_swim, full_route, part_start_route_clean_water, part_end_route_clean_water, time_swim_self, time_swim_with_icebreaker, time_all_order, status, type_route)
            VALUES ({order_id}, {point_start_id}, {point_end_id}, {point_start_id_icebreaker}, {point_end_id_icebreaker}, '{date}', null, null, null, null, null, null, 0, {type_route})
        """
        conn.execute_query(query)
    conn.close()



if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
