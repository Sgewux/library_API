from fastapi import FastAPI

from routers import books, subscribers

app = FastAPI()

app.include_router(books.router)
app.include_router(subscribers.router)
