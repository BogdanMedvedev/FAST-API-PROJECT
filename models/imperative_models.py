"""
Императивный - не допускающий выбора, требующий безусловного подчинения, исполнения.
мперативный стиль предполагает определение таблиц непосредственно с использованием языка Python.
Объекты таблиц, столбцов, индексов и ограничений создаются напрямую в коде Python с помощью классов
и методов SQLAlchemy. Этот стиль более прямолинеен и ближе к стандартному программированию на Python.
"""
import datetime

from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, Enum, text, DateTime

from models.enums import WorkLoad

table_metadata = MetaData()


# Объявление таблицы workers
workers_table = Table(
    'workers',
    table_metadata,
    Column(
        'id', Integer, primary_key=True, comment='Уникальный идентификатор работника'
    ),
    Column('username', String, comment='Имя пользователя'),
    # Добавление комментария для всей таблицы
    **{'comment': 'Работники'}
)

# Объявление таблицы resumes
resumes_table = Table(
    'resumes',
    table_metadata,
    Column('id', Integer, primary_key=True, comment='Уникальный идентификатор резюме'),
    Column('title', String(256), nullable=False, comment='Заголовок резюме'),
    Column('salary', Integer, nullable=True, comment='Заработная плата'),
    Column(
        'workload',
        Enum(WorkLoad),
        nullable=False,
        comment='Тип занятости (например, fulltime, parttime)',
    ),
    Column(
        'worker_id',
        Integer,
        ForeignKey('workers.id', ondelete='CASCADE'),
        nullable=False,
        comment='Идентификатор работника, к которому привязано резюме',
    ),
    Column(
        'created_at',
        DateTime,
        server_default=text("TIMEZONE('utc', now())"),
        comment='Дата и время создания резюме',
    ),
    Column(
        'update_at',
        DateTime,
        server_default=text("TIMEZONE('utc', now())"),
        onupdate=datetime.datetime.utcnow(),
        comment='Дата и время последнего обновления резюме',
    ),
    **{'comment': 'Резюме'}
)
