"""
Примеры CORE SQL-запросов
"""

from abc import ABC, abstractmethod

from sqlalchemy import text, insert, select, update

from databases_queries import engine
from models.imperative_models import table_metadata, workers_table


class CoreSQLRequests(ABC):
    """Примеры CORE SQL-запросов"""

    @staticmethod
    async def recreate_tables():
        """Пересоздание таблиц"""
        table_metadata.drop_all(bind=engine)
        table_metadata.create_all(bind=engine)

    @staticmethod
    @abstractmethod
    async def insert_data():
        """Вставка данных"""

    @staticmethod
    @abstractmethod
    async def select_data():
        """Выборка данных"""

    @staticmethod
    @abstractmethod
    async def update_data():
        """Обновление данных"""


class RawSQL(CoreSQLRequests):
    """Примеры сырых SQL-запросов"""

    @staticmethod
    async def insert_data():
        with engine.connect() as conn:
            sql_request = (
                """insert into workers (username) values ('Bobr') , ('Volk');"""
            )
            conn.execute(text(sql_request))
            conn.commit()

    @staticmethod
    async def select_data():
        with engine.connect() as conn:
            sql_request = """select * from workers;"""
            result = conn.execute(text(sql_request))
            workers = result.all()
        return workers

    @staticmethod
    async def update_data():
        worker_id = 1
        new_username = 'Ivan'
        with engine.connect() as conn:
            sql_request = text(
                """update workers set username=:username where id=:id;"""
            ).bindparams(username=new_username, id=worker_id)  # bindparams - защита от SQL-инъекций
            conn.execute(sql_request)
            conn.commit()


class QueryBuilderSQL(CoreSQLRequests):
    """Примеры SQL-запросов на основе query builder"""

    @staticmethod
    async def insert_data():
        """Пример query_builder SQL-запроса"""
        with engine.connect() as conn:
            sql_request = insert(workers_table).values(
                [{'username': 'Bobr'}, {'username': 'Volk'}]
            )
            conn.execute(sql_request)
            conn.commit()

    @staticmethod
    async def select_data():
        with engine.connect() as conn:
            query = select(workers_table)
            query_result = conn.execute(query)
            workers = query_result.all()
        return workers

    @staticmethod
    async def update_data():
        worker_id = 1
        new_username = 'Ivan'
        with engine.connect() as conn:
            query = (
                update(workers_table)
                .values(username=new_username)
                .filter_by(id=worker_id)
            )
            conn.execute(query)
            conn.commit()


async def apply_queries():
    """Применение методов CoreSQLRequests"""
    for class_obj in CoreSQLRequests.__subclasses__():
        await class_obj.recreate_tables()
        await class_obj.insert_data()
        await class_obj.update_data()
        print(class_obj.select_data())
