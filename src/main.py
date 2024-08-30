from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from api import router


app = FastAPI()
# app.add_middleware(SessionMiddleware, secret_key="!secret")

origins = [
    settings.front.url
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(
        "main:main_app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )
