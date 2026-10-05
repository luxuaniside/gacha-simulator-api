from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.api.banners import router as banners_router
from app.api.goals import router as goals_router
from app.api.simulation import router as simulation_router
from app.errors import (
    APIException,
    api_exception_handler,
    validation_exception_handler,
)

import uvicorn


app = FastAPI()


# Exception handlers
app.add_exception_handler(
    APIException,
    api_exception_handler,
)

app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler,
)


# CORS configuration
origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://192.168.0.139:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routers
app.include_router(banners_router)
app.include_router(goals_router)
app.include_router(simulation_router)


@app.get("/")
def home():
    return {"message": "API running"}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )