from fastapi import HTTPException

class ManagerIcebreakers:
    def __init__(self, settings, connector):
        self.settings = settings
        self.connector = connector

    async def get_icebreakers(self):
        query = f"SELECT * FROM {self.settings.db_name_table_icebreakers}"
        try:
            result = await self.connector.get_data_async(query)
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Description err - {e}")
        return result

    async def create_icebreaker(self, request):
        query = f"""
            INSERT INTO {self.settings.db_name_table_icebreakers} (name_icebreaker, class_icebreaker, speed, start_position)
            VALUES ('{request.name_icebreaker}', '{request.class_icebreaker}', '{request.speed}', '{request.start_position}')
        """
        try:
            await self.connector.execute_query_async(query)
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Description err - {e}")
        result = await self.connector.get_data_async(f"SELECT id FROM {self.settings.db_name_table_icebreakers} ORDER BY id DESC LIMIT 1")
        return {"status": "ok", "icebreaker_id": result[0]["id"]}

    async def delete_icebreaker(self, order_id: int):
        query = f"DELETE FROM {self.settings.db_name_table_icebreakers} WHERE id={order_id}"
        try:
            await self.connector.execute_query_async(query)
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Description err - {e}")
        return {"status": "ok"}
