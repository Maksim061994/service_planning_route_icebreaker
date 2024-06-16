from typing import Optional
from fastapi import HTTPException
from app.workers.tasks import add_order_to_table_task


class ManagerOrders:
    def __init__(self, settings, connector):
        self.settings = settings
        self.connector = connector

    async def get_orders(self, date_start: Optional = None, date_end: Optional = None):
        if date_start and date_end:
            query = f"SELECT * FROM {self.settings.db_name_table_orders} WHERE date_start_swim BETWEEN '{date_start}' AND '{date_end}'"
        elif date_start:
            query = f"SELECT * FROM {self.settings.db_name_table_orders} WHERE date_start_swim >= '{date_start}'"
        elif date_end:
            query = f"SELECT * FROM {self.settings.db_name_table_orders} WHERE date_start_swim <= '{date_end}'"
        else:
            query = f"SELECT * FROM {self.settings.db_name_table_orders}"
        try:
            result = await self.connector.get_data_async(query)
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Description err - {e}")
        return result

    async def create_order(self, request):
        order_id = request.order_id
        if order_id is None:
            query = f"""
                INSERT INTO {self.settings.db_name_table_orders} (name_ship, class_ship, point_start, point_end, speed, date_start_swim)
                VALUES ('{request.name_ship}', '{request.class_ship}', '{request.point_start}', '{request.point_end}', {request.speed}, '{request.date_start_swim}')
                ON CONFLICT (name_ship)
                DO UPDATE SET
                    speed = EXCLUDED.speed, 
                    date_start_swim = EXCLUDED.date_start_swim, 
                    point_start = EXCLUDED.point_start, 
                    point_end = EXCLUDED.point_end
            """
            try:
                await self.connector.execute_query_async(query)
            except Exception as e:
                raise HTTPException(status_code=404, detail=f"Description err - {e}")
            order = await self.connector.get_data_async(f"SELECT id FROM {self.settings.db_name_table_orders} WHERE name_ship = '{request.name_ship}'")
            order_id = order[0]["id"]
        task = add_order_to_table_task.delay(order_id)
        return {"status": "ok", "order_id": order_id, "task_id": task.task_id}


    async def __check_exits_order(self, request):
        query = f"SELECT * FROM {self.settings.db_name_table_orders} WHERE name_ship='{request.name_ship}' AND class_ship='{request.class_ship}' AND point_start='{request.point_start}' AND point_end='{request.point_end}' AND date_start_swim='{request.date_start_swim}'"
        try:
            result = await self.connector.get_data_async(query)
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Description err - {e}")
        return result

    async def delete_order(self, order_id: int):
        query = f"DELETE FROM {self.settings.db_name_table_orders} WHERE id={order_id}"
        try:
            await self.connector.execute_query_async(query)
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Description err - {e}")
        return {"status": "ok"}
