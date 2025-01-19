from fastapi import HTTPException
from databases_queries.declarative import DeclarativeSQLQuery
from fastapi import APIRouter


core_router = APIRouter()


@core_router.get(
    path='/workers',
    tags=['Работники'],
    summary='Получение списка работников'
)
async def get_workers():
    return await DeclarativeSQLQuery.convert_workers_to_dto()


@core_router.get(
    path='/resumes',
    tags=['Работники'],
    summary='Получение списка резюме'
)
async def get_workers():
    return await DeclarativeSQLQuery.select_resumes_with_all_relationships()


# @app.post(
#     path='/books',
#     tags=['Книги'],
#     summary='Создание книги'
# )
# def create_book(new_book: NewBook):
#     books.append(
#         {
#             'id': len(books) + 1,
#             'title': new_book.title,
#             'author': new_book.author,
#         }
#     )
#     return new_book
#
# @app.get(
#     path='/books/{book_id}',
#     tags=['Книги'],
#     summary='Получение книги по идентификатору'
# )
# def get_book(book_id: int):
#     for book in books:
#         if book['id'] == book_id:
#             return book
#     raise HTTPException(404, 'нет')
