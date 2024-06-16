import pickle
import pandas as pd
from app.helpers.connector_pgsql import PostgresConnector
from tqdm import tqdm


async def main():
    with open('data/full_graph_new.pickle', 'rb') as f:
        full_graph = pickle.load(f)
    conn = PostgresConnector(
        host="localhost", user="test", password="test",
        dbname="ship_tracking", port=5432
    )
    conn.connect()
    parameter = await conn.get_data_async("select * from parameters where name='date_start'")
    date_start = pd.to_datetime(parameter[0]['value'])

    for k in tqdm(full_graph):
        order_id = k[0]
        points_start_id = k[1]
        points_end_id = k[2]
        datetime = date_start + pd.Timedelta(hours=k[3])
        type_ship = k[4]
        query = f"""
            INSERT INTO graph_ships (order_id, points_start_id, points_end_id, datetime, type, time_swim)
            VALUES ({order_id}, {points_start_id}, {points_end_id}, '{datetime}', '{type_ship}', {full_graph[k]})
        """
        conn.execute_query(query)
    conn.close()



if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
