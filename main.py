from fastapi import FastAPI

from routers import books, categories, subscribers, authors, loans, librarians

app = FastAPI()

app.include_router(books.router)
app.include_router(loans.router)
app.include_router(authors.router)
app.include_router(librarians.router)
app.include_router(categories.router)
app.include_router(subscribers.router)