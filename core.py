from fastapi import HTTPException
from pydantic import BaseModel

from main import app


class NewBook(BaseModel):

    title: str
    author: str


books = [
    {
        'id': 1,
        'title': 'Асинхронность в Python',
        'author': 'Мэттью',
    },
    {
        'id': 2,
        'title': 'Бэкенд на Python',
        'author': 'Богдан',
    }
]

@app.get(
    path='/books',
    tags=['Книги'],
    summary='Получение списка книг'
)
def get_books():
    return books


@app.post(
    path='/books',
    tags=['Книги'],
    summary='Создание книги'
)
def create_book(new_book: NewBook):
    books.append(
        {
            'id': len(books) + 1,
            'title': new_book.title,
            'author': new_book.author,
        }
    )
    return new_book

@app.get(
    path='/books/{book_id}',
    tags=['Книги'],
    summary='Получение книги по идентификатору'
)
def get_book(book_id: int):
    for book in books:
        if book['id'] == book_id:
            return book
    raise HTTPException(404, 'нет')
