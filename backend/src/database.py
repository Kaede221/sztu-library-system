from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import enum

# SQLite 数据库文件
DATABASE_URL = "sqlite:///./library.db"

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# 创建SessionLocal类，用于创建数据库会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建Base类，用于ORM模型
Base = declarative_base()


# 用户角色枚举
class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


# 定义用户模型
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    role = Column(String(20), default=UserRole.USER.value, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


# 定义图书模型
class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    preview_image = Column(String)
    book_number = Column(String, unique=True, index=True)
    shelf_location = Column(String)
    quantity = Column(Integer)


# 获取数据库会话的依赖函数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 创建数据库表的函数
def create_tables():
    Base.metadata.create_all(bind=engine)


# 初始化数据库和表
create_tables()