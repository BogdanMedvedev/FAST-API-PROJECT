import logging
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload, load_only

from databases_queries import depends_session
from fastapi import APIRouter

from models.declarative_models import WorkersOrm, ResumesOrm, VacanciesOrm
from models.schemas import WorkersAddDTO, M2MResumesVacanciesDTO, WorkersRelDTO, ResumesDTO, WorkersDTO

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

core_router = APIRouter()


@core_router.get(
    path='/workers',
    tags=['Работники'],
    summary='Получение списка работников'
)
async def get_workers(session: depends_session):
    query = (
        select(WorkersOrm)
        .options(
            load_only(WorkersOrm.id, WorkersOrm.username),
            selectinload(WorkersOrm.resumes)
        )
        .limit(3)
    )
    res = await session.execute(query)
    result_orm = res.scalars().all()
    response = [WorkersRelDTO.model_validate(row, from_attributes=True) for row in result_orm]
    return response


@core_router.get(
    path='/resumes',
    tags=['Работники'],
    summary='Получение списка резюме'
)
async def get_resumes(session: depends_session):
    query = (
        select(ResumesOrm)
        .options(joinedload(ResumesOrm.worker))
        .options(selectinload(ResumesOrm.vacancies_replied).load_only(VacanciesOrm.title))
    )
    res = await session.execute(query)
    result_orm = res.unique().scalars().all()
    result_dto = [M2MResumesVacanciesDTO.model_validate(row, from_attributes=True) for row in result_orm]
    return result_dto


@core_router.post(
    path='/workers',
    tags=['Работники'],
    summary='Добавление работника',
    status_code=status.HTTP_201_CREATED
)
async def create_worker(data: WorkersAddDTO, session: depends_session):
    worker = WorkersOrm(
        **data.model_dump()
    )
    session.add(worker)
    await session.flush()
    logger.debug(f'Добавлен работник с ID: {worker.id}')
    await session.commit()
    return 'OK'


@core_router.get(
    path='/resumes/{resume_id}',
    tags=['Работники'],
    summary='Получение резюме по идентификатору'
)
async def get_resume(resume_id: int, session: depends_session):
    result = await session.get(entity=ResumesOrm, ident=resume_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Резюме с идентификатором {resume_id} не найдено")
    response = ResumesDTO.model_validate(result, from_attributes=True)
    return response
