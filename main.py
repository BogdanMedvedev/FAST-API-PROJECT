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


if __name__ == '__main__':
    DeclarativeSQLQuery.recreate_tables()
    # DeclarativeSQLQuery.insert_data()
    # DeclarativeSQLQuery.update_data()
    # DeclarativeSQLQuery.select_data()
    # DeclarativeSQLQuery.insert_additional_resumes()
    # DeclarativeSQLQuery.add_vacancies_and_replies()
    # DeclarativeSQLQuery.select_resumes_with_all_relationships()
    uvicorn.run('main:app', reload=True)
