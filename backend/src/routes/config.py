"""
系统配置管理路由模块
包含系统配置的CRUD操作
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ..database import get_db, User, SystemConfig
from ..schemas import (
    SystemConfigCreate,
    SystemConfigUpdate,
    SystemConfigResponse,
    SystemConfigListResponse,
    MessageResponse,
)
from ..auth import get_current_active_user, get_current_admin_user

# 创建路由
router = APIRouter()

# 默认配置
DEFAULT_CONFIGS = {
    "borrow_days": {"value": "30", "description": "默认借阅天数"},
    "max_borrow_count": {"value": "5", "description": "用户最大借阅数量"},
    "max_renew_count": {"value": "2", "description": "最大续借次数"},
    "renew_days": {"value": "14", "description": "续借天数"},
    "reservation_expire_days": {"value": "3", "description": "预约到书后的取书期限（天）"},
    "daily_fine": {"value": "0.5", "description": "每日逾期罚款金额（元）"},
    "library_name": {"value": "图书馆管理系统", "description": "图书馆名称"},
    "library_address": {"value": "", "description": "图书馆地址"},
    "library_phone": {"value": "", "description": "图书馆联系电话"},
    "library_email": {"value": "", "description": "图书馆邮箱"},
    "open_time": {"value": "08:00-22:00", "description": "开放时间"},
    "announcement": {"value": "", "description": "系统公告"},
}


# ==================== 配置查询接口 ====================

@router.get("/list", response_model=SystemConfigListResponse)
def get_all_configs(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取所有系统配置
    """
    configs = db.query(SystemConfig).order_by(SystemConfig.config_key.asc()).all()
    return SystemConfigListResponse(configs=configs)


@router.get("/{config_key}", response_model=SystemConfigResponse)
def get_config(
    config_key: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取指定配置
    """
    config = db.query(SystemConfig).filter(SystemConfig.config_key == config_key).first()
    if not config:
        # 如果配置不存在，检查是否有默认值
        if config_key in DEFAULT_CONFIGS:
            return SystemConfigResponse(
                id=0,
                config_key=config_key,
                config_value=DEFAULT_CONFIGS[config_key]["value"],
                description=DEFAULT_CONFIGS[config_key]["description"],
                updated_at=None
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="配置不存在"
        )
    return config


@router.get("/value/{config_key}")
def get_config_value(
    config_key: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取配置值（简化接口）
    """
    config = db.query(SystemConfig).filter(SystemConfig.config_key == config_key).first()
    if config:
        return {"key": config_key, "value": config.config_value}
    
    # 返回默认值
    if config_key in DEFAULT_CONFIGS:
        return {"key": config_key, "value": DEFAULT_CONFIGS[config_key]["value"]}
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="配置不存在"
    )


# ==================== 配置管理接口（管理员权限） ====================

@router.post("/create", response_model=SystemConfigResponse, status_code=status.HTTP_201_CREATED)
def create_config(
    config_data: SystemConfigCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    创建新配置（管理员权限）
    """
    # 检查配置是否已存在
    existing = db.query(SystemConfig).filter(
        SystemConfig.config_key == config_data.config_key
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="配置已存在"
        )
    
    # 创建配置
    config = SystemConfig(
        config_key=config_data.config_key,
        config_value=config_data.config_value,
        description=config_data.description
    )
    
    db.add(config)
    db.commit()
    db.refresh(config)
    
    return config


@router.put("/{config_key}", response_model=SystemConfigResponse)
def update_config(
    config_key: str,
    config_data: SystemConfigUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    更新配置（管理员权限）
    """
    config = db.query(SystemConfig).filter(SystemConfig.config_key == config_key).first()
    
    if not config:
        # 如果配置不存在但有默认值，则创建
        if config_key in DEFAULT_CONFIGS:
            config = SystemConfig(
                config_key=config_key,
                config_value=config_data.config_value,
                description=config_data.description or DEFAULT_CONFIGS[config_key]["description"]
            )
            db.add(config)
            db.commit()
            db.refresh(config)
            return config
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="配置不存在"
        )
    
    # 更新配置
    config.config_value = config_data.config_value
    if config_data.description is not None:
        config.description = config_data.description
    
    db.commit()
    db.refresh(config)
    
    return config


@router.delete("/{config_key}", response_model=MessageResponse)
def delete_config(
    config_key: str,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    删除配置（管理员权限）
    """
    config = db.query(SystemConfig).filter(SystemConfig.config_key == config_key).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="配置不存在"
        )
    
    db.delete(config)
    db.commit()
    
    return MessageResponse(message="配置删除成功")


# ==================== 批量操作接口 ====================

@router.post("/init-defaults", response_model=MessageResponse)
def init_default_configs(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    初始化默认配置（管理员权限）
    
    将所有默认配置写入数据库（不覆盖已存在的配置）
    """
    count = 0
    for key, data in DEFAULT_CONFIGS.items():
        existing = db.query(SystemConfig).filter(SystemConfig.config_key == key).first()
        if not existing:
            config = SystemConfig(
                config_key=key,
                config_value=data["value"],
                description=data["description"]
            )
            db.add(config)
            count += 1
    
    db.commit()
    
    return MessageResponse(message=f"已初始化 {count} 个默认配置")


@router.put("/batch-update", response_model=MessageResponse)
def batch_update_configs(
    configs: List[SystemConfigCreate],
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    批量更新配置（管理员权限）
    """
    count = 0
    for config_data in configs:
        config = db.query(SystemConfig).filter(
            SystemConfig.config_key == config_data.config_key
        ).first()
        
        if config:
            config.config_value = config_data.config_value
            if config_data.description:
                config.description = config_data.description
        else:
            config = SystemConfig(
                config_key=config_data.config_key,
                config_value=config_data.config_value,
                description=config_data.description
            )
            db.add(config)
        
        count += 1
    
    db.commit()
    
    return MessageResponse(message=f"已更新 {count} 个配置")


# ==================== 辅助函数 ====================

def get_config_value_helper(db: Session, config_key: str, default: str = "") -> str:
    """
    获取配置值的辅助函数（供其他模块使用）
    """
    config = db.query(SystemConfig).filter(SystemConfig.config_key == config_key).first()
    if config:
        return config.config_value
    
    if config_key in DEFAULT_CONFIGS:
        return DEFAULT_CONFIGS[config_key]["value"]
    
    return default


def get_config_int(db: Session, config_key: str, default: int = 0) -> int:
    """
    获取整数配置值
    """
    value = get_config_value_helper(db, config_key, str(default))
    try:
        return int(value)
    except ValueError:
        return default


def get_config_float(db: Session, config_key: str, default: float = 0.0) -> float:
    """
    获取浮点数配置值
    """
    value = get_config_value_helper(db, config_key, str(default))
    try:
        return float(value)
    except ValueError:
        return default