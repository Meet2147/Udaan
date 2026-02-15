from fastapi import APIRouter

from app.api.routes import admin, ai, auth, me, media, student, super_admin

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(me.router)
api_router.include_router(admin.router)
api_router.include_router(super_admin.router)
api_router.include_router(student.router)
api_router.include_router(ai.router)
api_router.include_router(media.router)
