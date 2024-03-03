from typing import Optional
from aiogram.filters.callback_data import CallbackData


class Project(CallbackData, prefix="proj"):
    types: str
    action: str
    num_proj: int = None
    id_proj: Optional[int] = None
    value: Optional[int] = None


class Reviews(CallbackData, prefix="reviews"):
    action: str
    review_num: Optional[int]
    value: Optional[int] = None
