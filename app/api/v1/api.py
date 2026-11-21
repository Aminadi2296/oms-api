from fastapi import APIRouter
from app.api.v1.endpoints import auth, clients, orders, stages, users

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(clients.router)
api_router.include_router(orders.router)
api_router.include_router(stages.router)
api_router.include_router(users.router)
