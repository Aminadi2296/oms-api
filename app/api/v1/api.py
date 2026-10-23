from fastapi import APIRouter
from app.api.v1.endpoints import auth, clients, stages

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(clients.router)
api_router.include_router(stages.router)
