"""
Примеры ORM SQL-запросов
"""
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from databases import engine
from models.declarative_models import WorkersOrm, Base


# сессия для взаимодействия с БД
session_factory = sessionmaker(engine)


class DeclarativeSQLRequests:
    """Примеры SQL-запросов с помощью ORM"""

    @staticmethod
    def recreate_tables():
        """Пересоздание таблиц"""
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

    @staticmethod
    def insert_data():
        """Вставка данных в таблицу работников"""
        workers = WorkersOrm(username='Alex'), WorkersOrm(username='Ivan')
        with session_factory() as session:
            session.add_all(workers)
            session.commit()

    @staticmethod
    def select_data():
        """Выборка данных"""
        with session_factory() as session:
            query = select(WorkersOrm)
            result = session.execute(query)
            workers = result.scalars().all()
        return workers

    @staticmethod
    def update_data():
        """Обновление данны"""

        pass


DeclarativeSQLRequests.recreate_tables()
DeclarativeSQLRequests.insert_data()
print(DeclarativeSQLRequests.select_data())