"""
Примеры ORM SQL-запросов
"""
from sqlalchemy import select, func, Integer, and_, insert
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import aliased, selectinload, contains_eager, joinedload
from databases_queries import engine
from models.declarative_models import WorkersOrm, Base, ResumesOrm, VacanciesOrm
from models.enums import WorkLoad
from models.schemas import WorkersRelDTO, M2MResumesVacanciesDTO


# сессия для взаимодействия с БД
session_factory = async_sessionmaker(engine)


class DeclarativeSQLQuery:
    """Примеры SQL-запросов с помощью ORM"""

    @staticmethod
    async def recreate_tables():
        """Пересоздание таблиц"""
        async with engine.begin() as connect:
            await connect.run_sync(Base.metadata.drop_all)
            await connect.run_sync(Base.metadata.create_all)

    @staticmethod
    async def insert_data():
        """Вставка данных в таблицу работников"""
        workers = WorkersOrm(username='Alex'), WorkersOrm(username='Ivan')
        async with session_factory() as session:
            session.add_all(workers)
            await session.commit()

    @staticmethod
    async def insert_resumes():
        """Содание резюме"""
        async with session_factory() as session:
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
            await session.commit()

    @staticmethod
    async def select_resumes_avg_salary(like_language: str = "Python"):
        """
        select workload, avg(salary)::int as avg_salary
        from resumes
        where title like '%Python%' and salary > 40000
        group by workload
        having avg(salary) > 70000
        """
        async with session_factory() as session:
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
            # вывод SQL запроса с конкретными значениями
            print(query.compile(compile_kwargs={"literal_binds": True}))
            res = await session.execute(query)
            result = res.all()
            print(result[0].avg_salary)
    
    @staticmethod
    async def insert_additional_resumes():
        async with session_factory() as session:
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
            await session.execute(insert_workers)
            await session.execute(insert_resumes)
            await session.commit()

    @staticmethod
    async def join_cte_subquery_window_func():
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
        async with session_factory() as session:
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
            res = await session.execute(query)
            print(res.all())

    @staticmethod
    async def select_data():
        """Выборка данных"""
        async with session_factory() as session:
            query = select(WorkersOrm)
            result = await session.execute(query)
            workers = result.scalars().all()
        print(workers)

    @staticmethod
    async def update_data():
        """Обновление данных"""
        worker_id = 1
        new_username = 'Ivan'
        async with session_factory() as session:
            worker_obj = await session.get(entity=WorkersOrm, ident=worker_id)
            worker_obj.username = new_username
            await session.commit()

    @staticmethod
    async def select_workers_with_selectin_relationship():
        async with session_factory() as session:
            query = (
                select(WorkersOrm)
                .options(selectinload(WorkersOrm.resumes))
            )

            res = await session.execute(query)
            result = res.scalars().all()
            print(result)
            worker_1_resumes = result[3].resumes
            print(worker_1_resumes)

            worker_2_resumes = result[4].resumes
            print(worker_2_resumes)

    @staticmethod
    async def select_workers_with_condition_relationship():
        async with session_factory() as session:
            query = (
                select(WorkersOrm)
                .options(selectinload(WorkersOrm.resumes_parttime))
                .options(selectinload(WorkersOrm.resumes_fulltime))
            )
            res = await session.execute(query)
            res = res.scalars().all()
            print(f'{res=}')

    @staticmethod
    async def select_workers_with_condition_relationship_contains_eager():
        """Вывод только тех сотрудников, у которых есть резюме c PARTTIME"""
        async with session_factory() as session:
            query = (
                select(WorkersOrm)
                .join(WorkersOrm.resumes)
                .options(contains_eager(WorkersOrm.resumes))
                .filter(ResumesOrm.workload == WorkLoad.PARTTIME)
            )

            res = await session.execute(query)
            result = res.unique().scalars().all()
            print(result)

    @staticmethod
    async def convert_workers_to_dto():
        async with session_factory() as session:
            query = (
                select(WorkersOrm)
                .options(selectinload(WorkersOrm.resumes))
                .limit(3)
            )

            res = await session.execute(query)
            result_orm = res.scalars().all()
            print(f"{result_orm=}")
            result_dto = [WorkersRelDTO.model_validate(row, from_attributes=True) for row in result_orm]
            print(f"{result_dto=}")
            return result_dto

    @staticmethod
    async def add_vacancies_and_replies():
        async with session_factory() as session:
            new_vacancy = VacanciesOrm(title="Python разработчик", compensation=100000)
            get_resume_1 = select(ResumesOrm).options(selectinload(ResumesOrm.vacancies_replied)).filter_by(id=1)
            get_resume_2 = select(ResumesOrm).options(selectinload(ResumesOrm.vacancies_replied)).filter_by(id=2)
            resume_1 = (await session.execute(get_resume_1)).scalar_one()
            resume_2 = (await session.execute(get_resume_2)).scalar_one()
            resume_1.vacancies_replied.append(new_vacancy)
            resume_2.vacancies_replied.append(new_vacancy)
            await session.commit()

    @staticmethod
    async def select_resumes_with_all_relationships():
        async with session_factory() as session:
            query = (
                select(ResumesOrm)
                .options(joinedload(ResumesOrm.worker))
                .options(selectinload(ResumesOrm.vacancies_replied).load_only(VacanciesOrm.title))
            )

            res = await session.execute(query)
            result_orm = res.unique().scalars().all()
            result_dto = [M2MResumesVacanciesDTO.model_validate(row, from_attributes=True) for row in result_orm]
            print(f"{result_dto=}")
            return result_dto
