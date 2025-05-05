from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request, HTTPException
from fastapi import FastAPI
from fastapi import status
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from typing import Annotated

from app.routers import brand
from app.routers import supplies
from app.routers import warehouse
from app.routers import temperature
from app.routers import location
from app.routers import stack
from app.routers import predict
from app.routers import current_predict

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware, secret_key="7UzGQS7woBazLUtVQJG39ywOP7J7lkPkB0UmDhMgBR8=" # :)
)

app.include_router(brand.router)
app.include_router(supplies.router)
app.include_router(warehouse.router)
app.include_router(temperature.router)
app.include_router(location.router)
app.include_router(stack.router)
app.include_router(predict.router)
app.include_router(current_predict.router)