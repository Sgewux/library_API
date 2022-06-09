from fastapi import FastAPI

from routers import books, subscribers, authors

app = FastAPI()

app.include_router(books.router)
app.include_router(authors.router)
app.include_router(subscribers.router)
