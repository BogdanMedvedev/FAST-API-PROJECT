"""
DTO (data transfer model). Модели для удобной работы с объектами БД и преобразования их в JSON.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from models.enums import WorkLoad


class WorkersAddDTO(BaseModel):
    """Модель для добавления записей в workers"""

    username: str


class WorkersDTO(WorkersAddDTO):
    """Модель для получения записей из workers"""

    id: int


class ResumesAddDTO(BaseModel):
    """Модель для добавления записей в resumes"""

    title: str
    salary: Optional[int]
    workload: WorkLoad
    worker_id: int


class ResumesDTO(ResumesAddDTO):
    """Модель для получения записей из resumes"""

    id: int
    created_at: datetime
    updated_at: datetime


class ResumesRelDTO(ResumesDTO):
    worker: "WorkersDTO"


class WorkersRelDTO(WorkersDTO):
    resumes: list[ResumesDTO]


class VacanciesAddDTO(BaseModel):
    title: str
    compensation: Optional[int]


class VacanciesDTO(VacanciesAddDTO):
    id: int


class VacanciesWithoutCompensationDTO(BaseModel):
    id: int
    title: str


class ResumesRelVacanciesRepliedDTO(ResumesDTO):
    worker: WorkersDTO
    vacancies_replied: list[VacanciesDTO]


class M2MResumesVacanciesDTO(ResumesDTO):
    worker: WorkersDTO
    vacancies_replied: list[VacanciesWithoutCompensationDTO]