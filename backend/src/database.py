from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Enum, ForeignKey, Text, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, date
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


# ==================== 枚举类型 ====================

# 用户角色枚举
class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


# 借阅状态枚举
class BorrowStatus(str, enum.Enum):
    BORROWED = "borrowed"      # 借阅中
    RETURNED = "returned"      # 已归还
    OVERDUE = "overdue"        # 已逾期


# 预约状态枚举
class ReservationStatus(str, enum.Enum):
    PENDING = "pending"        # 等待中
    AVAILABLE = "available"    # 可取书
    COMPLETED = "completed"    # 已完成
    CANCELLED = "cancelled"    # 已取消
    EXPIRED = "expired"        # 已过期


# 通知类型枚举
class NotificationType(str, enum.Enum):
    BORROW_DUE = "borrow_due"           # 借阅到期提醒
    RESERVATION_READY = "reservation_ready"  # 预约到书通知
    OVERDUE = "overdue"                 # 逾期通知
    SYSTEM = "system"                   # 系统公告


# ==================== 数据模型 ====================

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
    max_borrow_count = Column(Integer, default=5, nullable=False)  # 最大借阅数量
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关系
    borrow_records = relationship("BorrowRecord", back_populates="user")
    reservations = relationship("Reservation", back_populates="user")
    reviews = relationship("BookReview", back_populates="user")
    favorites = relationship("Favorite", back_populates="user")
    notifications = relationship("Notification", back_populates="user")


# 定义图书分类模型
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 自引用关系（多级分类）
    parent = relationship("Category", remote_side=[id], backref="children")
    books = relationship("Book", back_populates="category")


# 定义图书模型
class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), index=True, nullable=False)
    preview_image = Column(String(500), nullable=True)
    book_number = Column(String(50), unique=True, index=True, nullable=False)
    shelf_location = Column(String(50), nullable=True)
    quantity = Column(Integer, default=0)
    available_quantity = Column(Integer, default=0)  # 可借数量
    
    # 新增字段
    author = Column(String(200), nullable=True, index=True)
    isbn = Column(String(20), unique=True, nullable=True, index=True)
    publisher = Column(String(200), nullable=True)
    publish_date = Column(Date, nullable=True)
    price = Column(Float, nullable=True)
    description = Column(Text, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    tags = Column(String(500), nullable=True)  # 逗号分隔的标签
    
    # 统计字段
    borrow_count = Column(Integer, default=0)  # 累计借阅次数
    avg_rating = Column(Float, default=0.0)    # 平均评分
    review_count = Column(Integer, default=0)  # 评论数量
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关系
    category = relationship("Category", back_populates="books")
    borrow_records = relationship("BorrowRecord", back_populates="book")
    reservations = relationship("Reservation", back_populates="book")
    reviews = relationship("BookReview", back_populates="book")
    favorites = relationship("Favorite", back_populates="book")


# 借阅记录模型
class BorrowRecord(Base):
    __tablename__ = "borrow_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    borrow_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    due_date = Column(DateTime, nullable=False)  # 应还日期
    return_date = Column(DateTime, nullable=True)  # 实际归还日期
    status = Column(String(20), default=BorrowStatus.BORROWED.value, nullable=False)
    renew_count = Column(Integer, default=0)  # 续借次数
    fine_amount = Column(Float, default=0.0)  # 罚款金额
    fine_paid = Column(Boolean, default=False)  # 罚款是否已支付
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 关系
    user = relationship("User", back_populates="borrow_records")
    book = relationship("Book", back_populates="borrow_records")


# 预约记录模型
class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    reservation_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    expire_date = Column(DateTime, nullable=True)  # 预约过期时间（可取书后的有效期）
    status = Column(String(20), default=ReservationStatus.PENDING.value, nullable=False)
    queue_position = Column(Integer, default=0)  # 队列位置
    notified = Column(Boolean, default=False)  # 是否已通知
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 关系
    user = relationship("User", back_populates="reservations")
    book = relationship("Book", back_populates="reservations")


# 图书评论模型
class BookReview(Base):
    __tablename__ = "book_reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5星评分
    content = Column(Text, nullable=True)
    is_visible = Column(Boolean, default=True)  # 是否可见（管理员可隐藏）
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关系
    user = relationship("User", back_populates="reviews")
    book = relationship("Book", back_populates="reviews")


# 收藏模型
class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 关系
    user = relationship("User", back_populates="favorites")
    book = relationship("Book", back_populates="favorites")


# 通知模型
class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    notification_type = Column(String(50), default=NotificationType.SYSTEM.value, nullable=False)
    is_read = Column(Boolean, default=False)
    related_id = Column(Integer, nullable=True)  # 关联的记录ID（如借阅记录ID）
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 关系
    user = relationship("User", back_populates="notifications")


# 操作日志模型
class OperationLog(Base):
    __tablename__ = "operation_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    username = Column(String(50), nullable=True)
    action = Column(String(100), nullable=False)  # 操作类型
    resource_type = Column(String(50), nullable=True)  # 资源类型（book, user等）
    resource_id = Column(Integer, nullable=True)  # 资源ID
    detail = Column(Text, nullable=True)  # 详细信息
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


# 系统配置模型
class SystemConfig(Base):
    __tablename__ = "system_configs"

    id = Column(Integer, primary_key=True, index=True)
    config_key = Column(String(100), unique=True, nullable=False)
    config_value = Column(Text, nullable=False)
    description = Column(String(500), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


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