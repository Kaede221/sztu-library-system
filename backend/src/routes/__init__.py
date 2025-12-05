"""
路由模块
"""

from . import user
from . import book
from . import category
from . import borrow
from . import reservation
from . import review
from . import favorite
from . import notification
from . import stats
from . import config

__all__ = [
    "user",
    "book", 
    "category",
    "borrow",
    "reservation",
    "review",
    "favorite",
    "notification",
    "stats",
    "config",
]