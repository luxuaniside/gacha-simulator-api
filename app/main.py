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
import logging
from datetime import datetime
from pathlib import Path


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
    "https://gacha-simulator-vtbh.onrender.com",
    "https://gacha-simulator-vtbh.onrender.com/",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_file = LOG_DIR / f"app_{timestamp}.log"

file_handler = logging.FileHandler(
    log_file,
    encoding="utf-8",
    delay=True,
)

console_handler = logging.StreamHandler()

formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logging.basicConfig(
    level=logging.DEBUG,
    handlers=[
        file_handler,
        console_handler,
    ],
)

logger = logging.getLogger(__name__)

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