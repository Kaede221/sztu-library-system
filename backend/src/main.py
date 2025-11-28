from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# 导入模块
from .routes import user, book
from .database import get_db, User, Book
from .auth import get_current_active_user

# 创建应用示例
app = FastAPI(
    title="图书馆管理后台",
    version="0.1.0",
    description="图书馆管理系统后端API，包含用户管理、图书管理等功能",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境请设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包括路由信息
app.include_router(user.router, prefix="/user", tags=["用户管理"])
app.include_router(book.router, prefix="/book", tags=["图书管理"])


# 根路由
@app.get("/", tags=["系统"])
def root():
    """API根路由，返回系统信息"""
    return {
        "message": "欢迎使用图书馆管理系统API",
        "version": "0.1.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


# 健康检查
@app.get("/health", tags=["系统"])
def health_check():
    """健康检查接口"""
    return {"status": "healthy"}


# 统计信息接口
@app.get("/stats", tags=["系统"])
def get_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取系统统计信息
    
    需要登录认证
    返回：
    - total_users: 总用户数
    - total_books: 总图书数
    - active_users: 活跃用户数
    """
    total_users = db.query(User).count()
    total_books = db.query(Book).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    
    return {
        "total_users": total_users,
        "total_books": total_books,
        "active_users": active_users
    }
