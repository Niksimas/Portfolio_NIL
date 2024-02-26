from typing import Optional
from aiogram.filters.callback_data import CallbackData


class Project(CallbackData, prefix="proj"):
    types: str
    action: str
    id_proj: Optional[int]
    value: Optional[int] = None


class Reviews(CallbackData, prefix="reviews"):
    action: str
    review_id: Optional[int]
    value: Optional[int] = None
