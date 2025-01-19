"""
Декларативный стиль предполагает, что код описывает, что должно быть сделано, но не как.
Определение таблиц выносится в классы Python, которые являются подклассами специального класса,
предоставляемого SQLAlchemy (declarative_base). Структура таблицы описывается с помощью декларативного
синтаксиса, а SQLAlchemy автоматически создаёт объекты таблиц на основе этих классов.
"""
import datetime
from typing import Annotated

from sqlalchemy import ForeignKey, text, String
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship

from models.enums import WorkLoad

intpk = Annotated[int, mapped_column(primary_key=True, comment='Уникальный идентификатор записи')]
created_at = Annotated[
    datetime.datetime, mapped_column(
        server_default=text("TIMEZONE('utc', now())"),
        comment='Дата и время создания записи'
    )
]
updated_at = Annotated[
    datetime.datetime, mapped_column(
        server_default=text("TIMEZONE('utc', now())"),
        onupdate=datetime.datetime.utcnow(),
        comment='Дата и время последнего обновления записи'
    )
]
str256 = Annotated[
    str, 256
]


class Base(DeclarativeBase):

    type_annotation_map = {
        str256: String(length=256)
    }


class WorkersOrm(Base):

    __tablename__ = 'workers'
    __table_args__ = {'comment': 'Работники'}

    id: Mapped[intpk]
    username: Mapped[str] = mapped_column(comment='Имя пользователя')

    resumes: Mapped[list["ResumesOrm"]] = relationship(
        back_populates="worker",
    )

    resumes_parttime: Mapped[list["ResumesOrm"]] = relationship(
        back_populates="worker",
        primaryjoin="and_(WorkersOrm.id == ResumesOrm.worker_id, ResumesOrm.workload == 'PARTTIME')",
        order_by="ResumesOrm.id.desc()",
    )

    resumes_fulltime: Mapped[list["ResumesOrm"]] = relationship(
        back_populates="worker",
        primaryjoin="and_(WorkersOrm.id == ResumesOrm.worker_id, ResumesOrm.workload == 'FULLTIME')",
        order_by="ResumesOrm.id.desc()",
    )

    def __repr__(self):
        return f'{__class__.__name__}(id: {self.id})'


class ResumesOrm(Base):

    __tablename__ = 'resumes'
    __table_args__ = {'comment': 'Резюме'}

    id: Mapped[intpk]
    title: Mapped[str256] = mapped_column(comment='Заголовок резюме')
    salary: Mapped[int | None] = mapped_column(comment='Заработная плата')
    workload: Mapped[WorkLoad] = mapped_column(comment='Рабочая нагрузка')
    worker_id: Mapped[int] = mapped_column(
        ForeignKey('workers.id', ondelete='CASCADE'),
        comment='Ссылка на ID работника, который создал резюме'
    )
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    worker: Mapped["WorkersOrm"] = relationship(
        back_populates="resumes",
    )
    vacancies_replied: Mapped[list["VacanciesOrm"]] = relationship(
        back_populates="resumes_replied",
        secondary="vacancies_replies",
    )

    def __repr__(self):
        return f'{__class__.__name__}(id: {self.id})'


class VacanciesOrm(Base):
    __tablename__ = "vacancies"

    id: Mapped[intpk]
    title: Mapped[str256]
    compensation: Mapped[int]

    resumes_replied: Mapped[list["ResumesOrm"]] = relationship(
        back_populates="vacancies_replied",
        secondary="vacancies_replies",
    )


class VacanciesRepliesOrm(Base):
    __tablename__ = "vacancies_replies"

    resume_id: Mapped[int] = mapped_column(
        ForeignKey("resumes.id", ondelete="CASCADE"),
        primary_key=True,
    )
    vacancy_id: Mapped[int] = mapped_column(
        ForeignKey("vacancies.id", ondelete="CASCADE"),
        primary_key=True,
    )

    cover_letter: Mapped[str|None]
