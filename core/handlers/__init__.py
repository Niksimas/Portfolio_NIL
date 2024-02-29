from aiogram import Router

from .basic import router as gen
from .add_reviews import router as add
from .view_projects import router as proj
from .view_reviews import router as review
from .form import subrouter as form

main_router = Router()

main_router.include_routers(gen, add, review, proj, form)
