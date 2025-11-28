"""
用户管理路由模块
包含用户注册、登录、CRUD操作和权限管理
"""

from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..database import get_db, User, UserRole
from ..schemas import (
    UserCreate,
    UserUpdate,
    UserUpdateByAdmin,
    UserResponse,
    UserListResponse,
    LoginRequest,
    Token,
    ChangePasswordRequest,
    MessageResponse,
)
from ..auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    authenticate_user,
    get_current_active_user,
    get_current_admin_user,
    get_user_by_username,
    get_user_by_email,
    get_user_by_id,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

router = APIRouter()


# ==================== 认证相关接口 ====================

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    用户注册
    
    - **username**: 用户名（3-50字符，唯一）
    - **email**: 邮箱地址（唯一）
    - **password**: 密码（至少6字符）
    - **full_name**: 全名（可选）
    """
    # 检查用户名是否已存在
    if get_user_by_username(db, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已被注册"
        )
    
    # 检查邮箱是否已存在
    if get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册"
        )
    
    # 创建新用户
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        role=UserRole.USER.value,
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    用户登录
    
    - **username**: 用户名或邮箱
    - **password**: 密码
    
    返回JWT访问令牌
    """
    user = authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not bool(user.is_active):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": str(user.id),  # JWT标准要求sub为字符串
            "username": user.username,
            "role": user.role
        },
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/login/form", response_model=Token)
def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2表单登录（用于Swagger UI测试）
    
    - **username**: 用户名或邮箱
    - **password**: 密码
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not bool(user.is_active):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": str(user.id),  # JWT标准要求sub为字符串
            "username": user.username,
            "role": user.role
        },
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


# ==================== 当前用户相关接口 ====================

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """
    获取当前登录用户信息
    
    需要Bearer Token认证
    """
    return current_user


@router.put("/me", response_model=UserResponse)
def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    更新当前用户信息
    
    可更新字段：
    - **username**: 用户名
    - **email**: 邮箱
    - **full_name**: 全名
    - **password**: 新密码
    """
    # 检查用户名是否被其他用户使用
    if user_data.username and user_data.username != str(current_user.username):
        existing_user = get_user_by_username(db, user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已被使用"
            )
        current_user.username = user_data.username
    
    # 检查邮箱是否被其他用户使用
    if user_data.email and user_data.email != str(current_user.email):
        existing_user = get_user_by_email(db, user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被使用"
            )
        current_user.email = user_data.email
    
    # 更新其他字段
    if user_data.full_name is not None:
        current_user.full_name = user_data.full_name
    
    if user_data.password:
        current_user.hashed_password = get_password_hash(user_data.password)
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.post("/me/change-password", response_model=MessageResponse)
def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    修改当前用户密码
    
    - **old_password**: 旧密码
    - **new_password**: 新密码（至少6字符）
    """
    # 验证旧密码
    if not verify_password(password_data.old_password, str(current_user.hashed_password)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码错误"
        )
    
    # 更新密码
    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()
    
    return MessageResponse(message="密码修改成功")


# ==================== 管理员用户管理接口 ====================

@router.get("/list", response_model=UserListResponse)
def get_all_users(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回记录数"),
    search: Optional[str] = Query(None, description="搜索关键词（用户名或邮箱）"),
    role: Optional[str] = Query(None, description="按角色筛选"),
    is_active: Optional[bool] = Query(None, description="按激活状态筛选"),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    获取所有用户列表（管理员权限）
    
    支持分页、搜索和筛选
    """
    query = db.query(User)
    
    # 搜索过滤
    if search:
        query = query.filter(
            (User.username.contains(search)) | (User.email.contains(search))
        )
    
    # 角色过滤
    if role:
        query = query.filter(User.role == role)
    
    # 激活状态过滤
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    # 获取总数
    total = query.count()
    
    # 分页
    users = query.offset(skip).limit(limit).all()
    
    return UserListResponse(total=total, users=users)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    根据ID获取用户信息（管理员权限）
    """
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdateByAdmin,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    更新用户信息（管理员权限）
    
    可更新字段：
    - **username**: 用户名
    - **email**: 邮箱
    - **full_name**: 全名
    - **password**: 新密码
    - **role**: 用户角色（user/admin）
    - **is_active**: 是否激活
    """
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 检查用户名是否被其他用户使用
    if user_data.username and user_data.username != str(user.username):
        existing_user = get_user_by_username(db, user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已被使用"
            )
        user.username = user_data.username
    
    # 检查邮箱是否被其他用户使用
    if user_data.email and user_data.email != str(user.email):
        existing_user = get_user_by_email(db, user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被使用"
            )
        user.email = user_data.email
    
    # 更新其他字段
    if user_data.full_name is not None:
        user.full_name = user_data.full_name
    
    if user_data.password:
        user.hashed_password = get_password_hash(user_data.password)
    
    if user_data.role is not None:
        user.role = user_data.role.value
    
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    
    db.commit()
    db.refresh(user)
    
    return user


@router.delete("/{user_id}", response_model=MessageResponse)
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    删除用户（管理员权限）
    
    注意：不能删除自己
    """
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己"
        )
    
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    db.delete(user)
    db.commit()
    
    return MessageResponse(message="用户删除成功")


@router.post("/create", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user_by_admin(
    user_data: UserCreate,
    role: str = Query("user", description="用户角色（user/admin）"),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    管理员创建用户
    
    可以指定用户角色
    """
    # 验证角色
    if role not in [UserRole.USER.value, UserRole.ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的角色值"
        )
    
    # 检查用户名是否已存在
    if get_user_by_username(db, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已被注册"
        )
    
    # 检查邮箱是否已存在
    if get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册"
        )
    
    # 创建新用户
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        role=role,
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


# ==================== 初始化管理员接口 ====================

@router.post("/init-admin", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def init_admin(db: Session = Depends(get_db)):
    """
    初始化管理员账户
    
    仅当系统中没有管理员时可用
    创建默认管理员账户：
    - 用户名: admin
    - 密码: admin123
    - 邮箱: admin@library.com
    """
    # 检查是否已存在管理员
    existing_admin = db.query(User).filter(User.role == UserRole.ADMIN.value).first()
    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="管理员账户已存在"
        )
    
    # 创建默认管理员
    hashed_password = get_password_hash("admin123")
    admin_user = User(
        username="admin",
        email="admin@library.com",
        hashed_password=hashed_password,
        full_name="系统管理员",
        role=UserRole.ADMIN.value,
        is_active=True
    )
    
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    
    return admin_user
