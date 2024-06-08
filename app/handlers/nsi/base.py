from app.helpers.connector_pgsql import PostgresConnector


class Nsi:
    """
    Get base data from Database
    """
    def __init__(self, settings, connector):
        self.settings = settings
        self.connector = connector

    async def get_edges(self):
        """
        Get edges from Database
        :return:
        """
        query = f"SELECT * FROM {self.settings.db_name_table_edges}"
        result = await self.connector.get_data_async(query)
        return result

    async def get_points(self):
        query = f"SELECT * FROM {self.settings.db_name_table_edges}"
        result = await self.connector.get_data_async(query)
        return result
