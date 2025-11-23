from pydantic import BaseModel
from typing import Optional

# 图书基础模型
class BookBase(BaseModel):
    name: str
    preview_image: Optional[str] = None
    book_number: str
    shelf_location: str
    quantity: int

# 创建图书时使用的模型
class BookCreate(BookBase):
    pass

# 更新图书时使用的模型
class BookUpdate(BaseModel):
    name: Optional[str] = None
    preview_image: Optional[str] = None
    book_number: Optional[str] = None
    shelf_location: Optional[str] = None
    quantity: Optional[int] = None

# 从数据库读取图书时使用的模型
class Book(BookBase):
    id: int

    class Config:
        orm_mode = True