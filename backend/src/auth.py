"""
认证和安全模块
包含密码加密、JWT Token生成和验证、权限控制等功能
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from .database import get_db, User, UserRole
from .schemas import TokenData

# ==================== 配置 ====================

# JWT配置
SECRET_KEY = "your-secret-key-here-please-change-in-production"  # 生产环境请更换为安全的密钥
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # Token有效期：24小时

# 密码加密配置
# 使用 sha256_crypt 作为替代方案，避免 bcrypt 库的兼容性问题
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

# OAuth2配置
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")


# ==================== 密码工具函数 ====================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """获取密码哈希值"""
    return pwd_context.hash(password)


# ==================== JWT Token工具函数 ====================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建JWT访问令牌
    
    Args:
        data: 要编码到token中的数据
        expires_delta: 过期时间增量
    
    Returns:
        编码后的JWT token字符串
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[TokenData]:
    """
    解码JWT访问令牌
    
    Args:
        token: JWT token字符串
    
    Returns:
        TokenData对象，如果解码失败返回None
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        username = payload.get("username")
        role = payload.get("role")
        if user_id is None:
            return None
        return TokenData(user_id=int(user_id), username=username, role=role)
    except JWTError:
        return None


# ==================== 用户认证依赖函数 ====================

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    获取当前登录用户
    
    Args:
        token: JWT token
        db: 数据库会话
    
    Returns:
        当前登录的用户对象
    
    Raises:
        HTTPException: 如果token无效或用户不存在
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = decode_access_token(token)
    if token_data is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    获取当前活跃用户（已激活的用户）
    
    Args:
        current_user: 当前登录用户
    
    Returns:
        当前活跃用户对象
    
    Raises:
        HTTPException: 如果用户未激活
    """
    if not bool(current_user.is_active):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    获取当前管理员用户
    
    Args:
        current_user: 当前活跃用户
    
    Returns:
        当前管理员用户对象
    
    Raises:
        HTTPException: 如果用户不是管理员
    """
    if str(current_user.role) != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员权限"
        )
    return current_user


# ==================== 用户服务函数 ====================

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    验证用户登录
    
    Args:
        db: 数据库会话
        username: 用户名或邮箱
        password: 密码
    
    Returns:
        验证成功返回用户对象，失败返回None
    """
    # 支持用户名或邮箱登录
    user = db.query(User).filter(
        (User.username == username) | (User.email == username)
    ).first()
    
    if not user:
        return None
    if not verify_password(password, str(user.hashed_password)):
        return None
    return user


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """根据用户名获取用户"""
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """根据邮箱获取用户"""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """根据ID获取用户"""
    return db.query(User).filter(User.id == user_id).first()