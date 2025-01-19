import asyncio

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.core import core_router
from databases_queries.declarative import DeclarativeSQLQuery


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"]
)
app.include_router(core_router)


async def main():
    await DeclarativeSQLQuery.recreate_tables()
    await DeclarativeSQLQuery.insert_data()
    await DeclarativeSQLQuery.update_data()
    await DeclarativeSQLQuery.select_data()
    await DeclarativeSQLQuery.insert_additional_resumes()
    await DeclarativeSQLQuery.add_vacancies_and_replies()
    await DeclarativeSQLQuery.select_resumes_with_all_relationships()


if __name__ == '__main__':
    asyncio.run(main())
    uvicorn.run('main:app', reload=True)
