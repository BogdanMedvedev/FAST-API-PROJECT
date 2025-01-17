"""
Примеры ORM SQL-запросов
"""
from sqlalchemy import select, func, Integer, and_, insert
from sqlalchemy.orm import sessionmaker, aliased
from databases import engine
from models.declarative_models import WorkersOrm, Base, ResumesOrm
from models.enums import WorkLoad

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
    def insert_resumes():
        """Содание резюме"""
        with session_factory() as session:
            resume_jack_1 = ResumesOrm(
                title='Python Junior Developer', salary=50000, workload=WorkLoad.FULLTIME, worker_id=1)
            resume_jack_2 = ResumesOrm(
                title='Python Разработчик', salary=150000, workload=WorkLoad.FULLTIME, worker_id=1)
            resume_michael_1 = ResumesOrm(
                title='Python Data Engineer', salary=250000, workload=WorkLoad.PARTTIME, worker_id=2)
            resume_michael_2 = ResumesOrm(
                title='Data Scientist', salary=300000, workload=WorkLoad.PARTTIME, worker_id=2)
            session.add_all([resume_jack_1, resume_jack_2,
                             resume_michael_1, resume_michael_2])
            session.commit()

    @staticmethod
    def select_resumes_avg_salary(like_language: str = "Python"):
        """
        select workload, avg(salary)::int as avg_salary
        from resumes
        where title like '%Python%' and salary > 40000
        group by workload
        having avg(salary) > 70000
        """
        with session_factory() as session:
            query = (
                select(
                    ResumesOrm.workload,
                    func.avg(ResumesOrm.salary).cast(Integer).label("avg_salary"),
                )
                .select_from(ResumesOrm)
                .filter(and_(
                    ResumesOrm.title.contains(like_language),
                    ResumesOrm.salary > 40000,
                ))
                .group_by(ResumesOrm.workload)
                .having(func.avg(ResumesOrm.salary) > 70000)
            )
            print(query.compile(compile_kwargs={"literal_binds": True}))
            res = session.execute(query)
            result = res.all()
            print(result[0].avg_salary)
    
    @staticmethod
    def insert_additional_resumes():
        with session_factory() as session:
            workers = [
                {"username": "Artem"},  # id 3
                {"username": "Roman"},  # id 4
                {"username": "Petr"},   # id 5
            ]
            resumes = [
                {"title": "Python программист", "salary": 60000, "workload": WorkLoad.FULLTIME, "worker_id": 3},
                {"title": "Machine Learning Engineer", "salary": 70000, "workload": WorkLoad.PARTTIME, "worker_id": 3},
                {"title": "Python Data Scientist", "salary": 80000, "workload": WorkLoad.PARTTIME, "worker_id": 4},
                {"title": "Python Analyst", "salary": 90000, "workload": WorkLoad.FULLTIME, "worker_id": 4},
                {"title": "Python Junior Developer", "salary": 100000, "workload": WorkLoad.FULLTIME, "worker_id": 5},
            ]
            insert_workers = insert(WorkersOrm).values(workers)
            insert_resumes = insert(ResumesOrm).values(resumes)
            session.execute(insert_workers)
            session.execute(insert_resumes)
            session.commit()

    @staticmethod
    def join_cte_subquery_window_func():
        """
        WITH helper2 AS (
            SELECT *, salary-avg_workload_salary AS salary_diff
            FROM 
            (SELECT
                w.id,
                w.username,
                r.salary,
                r.workload,
                avg(r.salary) OVER (PARTITION BY workload)::int AS avg_workload_salary
            FROM resumes r
            JOIN workers w ON r.worker_id = w.id) helper1
        )
        SELECT * FROM helper2
        ORDER BY salary_diff DESC;
        """
        with session_factory() as session:
            r = aliased(ResumesOrm)
            w = aliased(WorkersOrm)
            subq = (
                select(
                    r,
                    w,
                    func.avg(r.salary).over(partition_by=r.workload).cast(Integer).label("avg_workload_salary"),
                )
                # .select_from(r)
                .join(r, r.worker_id == w.id).subquery("helper1")
            )
            cte = (
                select(
                    subq.c.worker_id,
                    subq.c.username,
                    subq.c.salary,
                    subq.c.workload,
                    subq.c.avg_workload_salary,
                    (subq.c.salary - subq.c.avg_workload_salary).label("salary_diff"),
                )
                .cte("helper2")
            )
            query = (
                select(cte)
                .order_by(cte.c.salary_diff.desc())
            )
            res = session.execute(query)
            print(res.all())

    @staticmethod
    def select_data():
        """Выборка данных"""
        with session_factory() as session:
            query = select(WorkersOrm)
            result = session.execute(query)
            workers = result.scalars().all()
        print(workers)

    @staticmethod
    def update_data():
        """Обновление данных"""
        worker_id = 1
        new_username = 'Ivan'
        with session_factory() as session:
            worker_obj = session.get(entity=WorkersOrm, ident=worker_id)
            worker_obj.username = new_username
            session.commit()


DeclarativeSQLRequests.recreate_tables()
DeclarativeSQLRequests.insert_data()
DeclarativeSQLRequests.update_data()
DeclarativeSQLRequests.select_data()
DeclarativeSQLRequests.insert_additional_resumes()
DeclarativeSQLRequests.join_cte_subquery_window_func()