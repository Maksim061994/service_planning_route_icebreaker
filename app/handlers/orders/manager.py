from typing import Optional
from fastapi import HTTPException


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
        query = f"""
            INSERT INTO {self.settings.db_name_table_orders} (name_ship, class_ship, point_start, point_end, speed, date_start_swim)
            VALUES ('{request.name_ship}', '{request.class_ship}', '{request.point_start}', '{request.point_end}', {request.speed}, '{request.date_start_swim}')
        """
        try:
            await self.connector.execute_query_async(query)
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Description err - {e}")
        result = await self.connector.get_data_async(f"SELECT id FROM {self.settings.db_name_table_orders} ORDER BY id DESC LIMIT 1")
        return {"status": "ok", "order_id": result[0]["id"]}

    async def delete_order(self, order_id: int):
        query = f"DELETE FROM {self.settings.db_name_table_orders} WHERE id={order_id}"
        try:
            await self.connector.execute_query_async(query)
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Description err - {e}")
        return {"status": "ok"}
