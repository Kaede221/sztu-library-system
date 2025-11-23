from fastapi import FastAPI

# 导入模块
from .routes import user, book

# 创建应用示例
app = FastAPI(title="图书馆管理后台", version="0.1.0")

# 包括路由信息
app.include_router(user.router, prefix="/user", tags=["用户管理"])
app.include_router(book.router, prefix="/book", tags=["图书管理"])
