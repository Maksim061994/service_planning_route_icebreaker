import psycopg2
import asyncpg
from loguru import logger


class PostgresConnector:
    def __init__(self, host, dbname, user, password, port=5432):
        self.host = host
        self.dbname = dbname
        self.user = user
        self.password = password
        self.port = port
        self.conn = None

    def connect(self):
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                port=self.port
            )
            logger.info("Successfully connected to the database")
        except psycopg2.Error as e:
            logger.error(f"An error occurred while connecting to the database: {e}")
            raise e

    def close(self):
        if self.conn is not None:
            self.conn.close()
            logger.info("Database connection closed")

    def execute_query(self, query):
        if self.conn is None:
            logger.error("You must connect to the database first")
            return
        try:
            cur = self.conn.cursor()
            cur.execute(query)
            self.conn.commit()
            logger.info("Query executed successfully")
        except psycopg2.Error as e:
            logger.error(f"An error occurred while executing the query: {e}")
            raise e

    async def get_data_async(self, query):
        conn = await asyncpg.connect(
            host=self.host,
            database=self.dbname,
            user=self.user,
            password=self.password,
            port=self.port
        )
        try:
            result = await conn.fetch(query)
            return result
        except Exception as e:
            logger.error(f"An error occurred while executing the query: {e}")
            raise e
        finally:
            await conn.close()

    async def execute_query_async(self, query):
        conn = await asyncpg.connect(
            host=self.host,
            database=self.dbname,
            user=self.user,
            password=self.password,
            port=self.port
        )
        try:
            await conn.execute(query)
            logger.info("Query executed successfully")
        except Exception as e:
            logger.error(f"An error occurred while executing the query: {e}")
            raise e
        finally:
            await conn.close()

