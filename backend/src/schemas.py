from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime, date
from enum import Enum


# ==================== 枚举类型 ====================

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class BorrowStatus(str, Enum):
    BORROWED = "borrowed"
    RETURNED = "returned"
    OVERDUE = "overdue"


class ReservationStatus(str, Enum):
    PENDING = "pending"
    AVAILABLE = "available"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class NotificationType(str, Enum):
    BORROW_DUE = "borrow_due"
    RESERVATION_READY = "reservation_ready"
    OVERDUE = "overdue"
    SYSTEM = "system"


# ==================== 用户相关模型 ====================

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    full_name: Optional[str] = Field(None, max_length=100, description="全名")


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100, description="密码")


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="用户名")
    email: Optional[EmailStr] = Field(None, description="邮箱地址")
    full_name: Optional[str] = Field(None, max_length=100, description="全名")
    password: Optional[str] = Field(None, min_length=6, max_length=100, description="新密码")
    is_active: Optional[bool] = Field(None, description="是否激活")


class UserUpdateByAdmin(UserUpdate):
    role: Optional[UserRole] = Field(None, description="用户角色")
    max_borrow_count: Optional[int] = Field(None, ge=0, le=20, description="最大借阅数量")


class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool
    max_borrow_count: int = 5
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    total: int
    users: List[UserResponse]


# ==================== 认证相关模型 ====================

class LoginRequest(BaseModel):
    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="过期时间（秒）")


class TokenData(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None
    role: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=100, description="新密码")


# ==================== 通用响应模型 ====================

class MessageResponse(BaseModel):
    message: str
    success: bool = True


# ==================== 分类相关模型 ====================

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="分类名称")
    description: Optional[str] = Field(None, description="分类描述")
    parent_id: Optional[int] = Field(None, description="父分类ID")
    sort_order: int = Field(0, description="排序顺序")


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="分类名称")
    description: Optional[str] = Field(None, description="分类描述")
    parent_id: Optional[int] = Field(None, description="父分类ID")
    sort_order: Optional[int] = Field(None, description="排序顺序")


class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class CategoryWithChildren(CategoryResponse):
    children: List["CategoryWithChildren"] = []


class CategoryListResponse(BaseModel):
    total: int
    categories: List[CategoryResponse]


class CategoryTreeResponse(BaseModel):
    categories: List[CategoryWithChildren]


# ==================== 图书相关模型 ====================

class BookBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="图书名称")
    book_number: str = Field(..., min_length=1, max_length=50, description="图书编号")
    shelf_location: Optional[str] = Field(None, max_length=50, description="书架位置")
    quantity: int = Field(0, ge=0, description="总数量")
    preview_image: Optional[str] = Field(None, max_length=500, description="预览图片URL")
    
    # 新增字段
    author: Optional[str] = Field(None, max_length=200, description="作者")
    isbn: Optional[str] = Field(None, max_length=20, description="ISBN")
    publisher: Optional[str] = Field(None, max_length=200, description="出版社")
    publish_date: Optional[date] = Field(None, description="出版日期")
    price: Optional[float] = Field(None, ge=0, description="价格")
    description: Optional[str] = Field(None, description="图书简介")
    category_id: Optional[int] = Field(None, description="分类ID")
    tags: Optional[str] = Field(None, max_length=500, description="标签（逗号分隔）")


class BookCreate(BookBase):
    available_quantity: Optional[int] = Field(None, ge=0, description="可借数量")


class BookUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="图书名称")
    book_number: Optional[str] = Field(None, min_length=1, max_length=50, description="图书编号")
    shelf_location: Optional[str] = Field(None, max_length=50, description="书架位置")
    quantity: Optional[int] = Field(None, ge=0, description="总数量")
    available_quantity: Optional[int] = Field(None, ge=0, description="可借数量")
    preview_image: Optional[str] = Field(None, max_length=500, description="预览图片URL")
    author: Optional[str] = Field(None, max_length=200, description="作者")
    isbn: Optional[str] = Field(None, max_length=20, description="ISBN")
    publisher: Optional[str] = Field(None, max_length=200, description="出版社")
    publish_date: Optional[date] = Field(None, description="出版日期")
    price: Optional[float] = Field(None, ge=0, description="价格")
    description: Optional[str] = Field(None, description="图书简介")
    category_id: Optional[int] = Field(None, description="分类ID")
    tags: Optional[str] = Field(None, max_length=500, description="标签（逗号分隔）")


class Book(BookBase):
    id: int
    available_quantity: int = 0
    borrow_count: int = 0
    avg_rating: float = 0.0
    review_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BookWithCategory(Book):
    category: Optional[CategoryResponse] = None


class BookListResponse(BaseModel):
    total: int
    books: List[Book]


class BookDetailResponse(BookWithCategory):
    """图书详情响应，包含分类信息"""
    pass


# ==================== 借阅相关模型 ====================

class BorrowRecordBase(BaseModel):
    book_id: int = Field(..., description="图书ID")


class BorrowCreate(BorrowRecordBase):
    user_id: Optional[int] = Field(None, description="用户ID（管理员代借时使用）")
    borrow_days: int = Field(30, ge=1, le=90, description="借阅天数")


class BorrowReturn(BaseModel):
    fine_paid: bool = Field(False, description="是否支付罚款")


class BorrowRenew(BaseModel):
    renew_days: int = Field(14, ge=1, le=30, description="续借天数")


class BorrowRecordResponse(BaseModel):
    id: int
    user_id: int
    book_id: int
    borrow_date: datetime
    due_date: datetime
    return_date: Optional[datetime] = None
    status: BorrowStatus
    renew_count: int
    fine_amount: float
    fine_paid: bool
    created_at: datetime

    class Config:
        from_attributes = True


class BorrowRecordWithDetails(BorrowRecordResponse):
    """借阅记录详情，包含用户和图书信息"""
    user: Optional[UserResponse] = None
    book: Optional[Book] = None


class BorrowRecordListResponse(BaseModel):
    total: int
    records: List[BorrowRecordResponse]


class BorrowRecordDetailListResponse(BaseModel):
    total: int
    records: List[BorrowRecordWithDetails]


# ==================== 预约相关模型 ====================

class ReservationCreate(BaseModel):
    book_id: int = Field(..., description="图书ID")


class ReservationCancel(BaseModel):
    reason: Optional[str] = Field(None, description="取消原因")


class ReservationResponse(BaseModel):
    id: int
    user_id: int
    book_id: int
    reservation_date: datetime
    expire_date: Optional[datetime] = None
    status: ReservationStatus
    queue_position: int
    notified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ReservationWithDetails(ReservationResponse):
    """预约记录详情，包含用户和图书信息"""
    user: Optional[UserResponse] = None
    book: Optional[Book] = None


class ReservationListResponse(BaseModel):
    total: int
    reservations: List[ReservationResponse]


class ReservationDetailListResponse(BaseModel):
    total: int
    reservations: List[ReservationWithDetails]


# ==================== 评论相关模型 ====================

class ReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="评分（1-5星）")
    content: Optional[str] = Field(None, description="评论内容")


class ReviewCreate(ReviewBase):
    book_id: int = Field(..., description="图书ID")


class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5, description="评分（1-5星）")
    content: Optional[str] = Field(None, description="评论内容")


class ReviewResponse(ReviewBase):
    id: int
    user_id: int
    book_id: int
    is_visible: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReviewWithUser(ReviewResponse):
    """评论详情，包含用户信息"""
    user: Optional[UserResponse] = None


class ReviewListResponse(BaseModel):
    total: int
    reviews: List[ReviewResponse]


class ReviewDetailListResponse(BaseModel):
    total: int
    reviews: List[ReviewWithUser]


# ==================== 收藏相关模型 ====================

class FavoriteCreate(BaseModel):
    book_id: int = Field(..., description="图书ID")


class FavoriteResponse(BaseModel):
    id: int
    user_id: int
    book_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class FavoriteWithBook(FavoriteResponse):
    """收藏详情，包含图书信息"""
    book: Optional[Book] = None


class FavoriteListResponse(BaseModel):
    total: int
    favorites: List[FavoriteResponse]


class FavoriteDetailListResponse(BaseModel):
    total: int
    favorites: List[FavoriteWithBook]


# ==================== 通知相关模型 ====================

class NotificationCreate(BaseModel):
    user_id: int = Field(..., description="用户ID")
    title: str = Field(..., min_length=1, max_length=200, description="通知标题")
    content: str = Field(..., description="通知内容")
    notification_type: NotificationType = Field(NotificationType.SYSTEM, description="通知类型")
    related_id: Optional[int] = Field(None, description="关联记录ID")


class NotificationBroadcast(BaseModel):
    """广播通知（发送给所有用户）"""
    title: str = Field(..., min_length=1, max_length=200, description="通知标题")
    content: str = Field(..., description="通知内容")


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    content: str
    notification_type: NotificationType
    is_read: bool
    related_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    total: int
    unread_count: int
    notifications: List[NotificationResponse]


# ==================== 操作日志相关模型 ====================

class OperationLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    username: Optional[str] = None
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[int] = None
    detail: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class OperationLogListResponse(BaseModel):
    total: int
    logs: List[OperationLogResponse]


# ==================== 系统配置相关模型 ====================

class SystemConfigBase(BaseModel):
    config_key: str = Field(..., min_length=1, max_length=100, description="配置键")
    config_value: str = Field(..., description="配置值")
    description: Optional[str] = Field(None, max_length=500, description="配置描述")


class SystemConfigCreate(SystemConfigBase):
    pass


class SystemConfigUpdate(BaseModel):
    config_value: str = Field(..., description="配置值")
    description: Optional[str] = Field(None, max_length=500, description="配置描述")


class SystemConfigResponse(SystemConfigBase):
    id: int
    updated_at: datetime

    class Config:
        from_attributes = True


class SystemConfigListResponse(BaseModel):
    configs: List[SystemConfigResponse]


# ==================== 统计相关模型 ====================

class DashboardStats(BaseModel):
    """仪表盘统计数据"""
    total_users: int
    total_books: int
    total_categories: int
    active_users: int
    total_borrow_records: int
    active_borrows: int
    overdue_borrows: int
    total_reservations: int
    pending_reservations: int


class BookRankingItem(BaseModel):
    """图书排行项"""
    book_id: int
    book_name: str
    author: Optional[str] = None
    borrow_count: int
    avg_rating: float


class BookRankingResponse(BaseModel):
    """图书排行榜响应"""
    rankings: List[BookRankingItem]


class UserBorrowStats(BaseModel):
    """用户借阅统计"""
    user_id: int
    username: str
    total_borrows: int
    current_borrows: int
    overdue_count: int
    total_fines: float


class MonthlyStats(BaseModel):
    """月度统计"""
    month: str
    borrow_count: int
    return_count: int
    new_users: int
    new_books: int


class MonthlyStatsResponse(BaseModel):
    """月度统计响应"""
    stats: List[MonthlyStats]


class CategoryStats(BaseModel):
    """分类统计"""
    category_id: int
    category_name: str
    book_count: int
    borrow_count: int


class CategoryStatsResponse(BaseModel):
    """分类统计响应"""
    stats: List[CategoryStats]