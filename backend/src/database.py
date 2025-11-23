from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

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

# 定义图书模型
class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    preview_image = Column(String)
    book_number = Column(String, unique=True, index=True)
    shelf_location = Column(String)
    quantity = Column(Integer)

# 创建数据库表的函数
def create_tables():
    Base.metadata.create_all(bind=engine)

# 初始化数据库和表
create_tables()