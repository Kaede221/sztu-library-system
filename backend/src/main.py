from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# 导入模块
from .routes import (
    user, book, category, borrow, reservation,
    review, favorite, notification, stats, config
)
from .database import get_db, User, Book, Category
from .auth import get_current_active_user

# 创建应用示例
app = FastAPI(
    title="图书馆管理后台",
    version="2.0.0",
    description="""
图书馆管理系统后端API

## 功能模块

* **用户管理** - 用户注册、登录、权限管理
* **图书管理** - 图书CRUD、搜索、分类
* **分类管理** - 多级分类、分类树
* **借阅管理** - 借书、还书、续借、逾期管理
* **预约管理** - 图书预约、预约队列
* **评论系统** - 图书评分、评论
* **收藏功能** - 图书收藏
* **通知系统** - 系统通知、消息推送
* **统计分析** - 借阅排行、月度报表
* **系统配置** - 系统参数配置
    """,
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
app.include_router(category.router, prefix="/category", tags=["分类管理"])
app.include_router(borrow.router, prefix="/borrow", tags=["借阅管理"])
app.include_router(reservation.router, prefix="/reservation", tags=["预约管理"])
app.include_router(review.router, prefix="/review", tags=["评论系统"])
app.include_router(favorite.router, prefix="/favorite", tags=["收藏功能"])
app.include_router(notification.router, prefix="/notification", tags=["通知系统"])
app.include_router(stats.router, prefix="/stats", tags=["统计分析"])
app.include_router(config.router, prefix="/config", tags=["系统配置"])


# 根路由
@app.get("/", tags=["系统"])
def root():
    """API根路由，返回系统信息"""
    return {
        "message": "欢迎使用图书馆管理系统API",
        "version": "2.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "features": [
            "用户管理",
            "图书管理",
            "分类管理",
            "借阅管理",
            "预约管理",
            "评论系统",
            "收藏功能",
            "通知系统",
            "统计分析",
            "系统配置"
        ]
    }


# 健康检查
@app.get("/health", tags=["系统"])
def health_check():
    """健康检查接口"""
    return {"status": "healthy"}


# 简单统计信息接口（保留向后兼容）
@app.get("/simple-stats", tags=["系统"])
def get_simple_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取简单统计信息（向后兼容）
    
    需要登录认证
    返回：
    - total_users: 总用户数
    - total_books: 总图书数
    - total_categories: 总分类数
    - active_users: 活跃用户数
    """
    total_users = db.query(User).count()
    total_books = db.query(Book).count()
    total_categories = db.query(Category).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    
    return {
        "total_users": total_users,
        "total_books": total_books,
        "total_categories": total_categories,
        "active_users": active_users
    }
