"""路由聚合"""
from fastapi import APIRouter

from api.v1 import users_api as users, notes_api as notes, verify_api as verify

api_router = APIRouter(prefix="/v1")
api_router.include_router(users.router)
api_router.include_router(notes.router)
api_router.include_router(verify.router)
