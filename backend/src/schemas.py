from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum


# ==================== 用户角色枚举 ====================
class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


# ==================== 用户相关模型 ====================

# 用户基础模型
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    full_name: Optional[str] = Field(None, max_length=100, description="全名")


# 用户创建模型（注册时使用）
class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100, description="密码")


# 用户更新模型
class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="用户名")
    email: Optional[EmailStr] = Field(None, description="邮箱地址")
    full_name: Optional[str] = Field(None, max_length=100, description="全名")
    password: Optional[str] = Field(None, min_length=6, max_length=100, description="新密码")
    is_active: Optional[bool] = Field(None, description="是否激活")


# 管理员更新用户模型（可以修改角色）
class UserUpdateByAdmin(UserUpdate):
    role: Optional[UserRole] = Field(None, description="用户角色")


# 用户响应模型（返回给前端）
class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 用户列表响应模型
class UserListResponse(BaseModel):
    total: int
    users: list[UserResponse]


# ==================== 认证相关模型 ====================

# 登录请求模型
class LoginRequest(BaseModel):
    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")


# Token响应模型
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="过期时间（秒）")


# Token数据模型（用于JWT payload）
class TokenData(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None
    role: Optional[str] = None


# 修改密码请求模型
class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=100, description="新密码")


# ==================== 通用响应模型 ====================

# 消息响应模型
class MessageResponse(BaseModel):
    message: str
    success: bool = True


# ==================== 图书相关模型 ====================

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
        from_attributes = True


# 图书列表响应模型
class BookListResponse(BaseModel):
    total: int
    books: list[Book]