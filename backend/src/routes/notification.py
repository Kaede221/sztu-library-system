"""
通知管理路由模块
包含通知的发送、查询和管理功能
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ..database import get_db, User, Notification, NotificationType
from ..schemas import (
    NotificationCreate,
    NotificationBroadcast,
    NotificationResponse,
    NotificationListResponse,
    MessageResponse,
)
from ..auth import get_current_active_user, get_current_admin_user

# 创建路由
router = APIRouter()


# ==================== 用户通知接口 ====================

@router.get("/my-notifications", response_model=NotificationListResponse)
def get_my_notifications(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回记录数"),
    unread_only: bool = Query(False, description="仅显示未读通知"),
    notification_type: Optional[str] = Query(None, description="通知类型筛选"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的通知列表
    """
    query = db.query(Notification).filter(Notification.user_id == current_user.id)
    
    # 未读筛选
    if unread_only:
        query = query.filter(Notification.is_read == False)
    
    # 类型筛选
    if notification_type:
        query = query.filter(Notification.notification_type == notification_type)
    
    # 排序（最新的在前）
    query = query.order_by(Notification.created_at.desc())
    
    # 获取总数
    total = query.count()
    
    # 获取未读数量
    unread_count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).count()
    
    # 分页
    notifications = query.offset(skip).limit(limit).all()
    
    return NotificationListResponse(
        total=total,
        unread_count=unread_count,
        notifications=notifications
    )


@router.get("/unread-count")
def get_unread_count(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取未读通知数量
    """
    count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).count()
    
    return {"unread_count": count}


@router.post("/mark-read/{notification_id}", response_model=NotificationResponse)
def mark_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    标记通知为已读
    """
    notification = db.query(Notification).filter(
        Notification.id == notification_id
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="通知不存在"
        )
    
    # 检查权限
    if notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作此通知"
        )
    
    notification.is_read = True
    db.commit()
    db.refresh(notification)
    
    return notification


@router.post("/mark-all-read", response_model=MessageResponse)
def mark_all_as_read(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    标记所有通知为已读
    """
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).update({"is_read": True})
    
    db.commit()
    
    return MessageResponse(message="已将所有通知标记为已读")


@router.delete("/{notification_id}", response_model=MessageResponse)
def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    删除通知
    """
    notification = db.query(Notification).filter(
        Notification.id == notification_id
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="通知不存在"
        )
    
    # 检查权限
    if notification.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此通知"
        )
    
    db.delete(notification)
    db.commit()
    
    return MessageResponse(message="通知删除成功")


@router.delete("/clear-all", response_model=MessageResponse)
def clear_all_notifications(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    清空所有通知
    """
    db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).delete()
    
    db.commit()
    
    return MessageResponse(message="已清空所有通知")


# ==================== 管理员接口 ====================

@router.post("/send", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
def send_notification(
    notification_data: NotificationCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    发送通知给指定用户（管理员权限）
    """
    # 检查目标用户是否存在
    target_user = db.query(User).filter(User.id == notification_data.user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="目标用户不存在"
        )
    
    # 创建通知
    notification = Notification(
        user_id=notification_data.user_id,
        title=notification_data.title,
        content=notification_data.content,
        notification_type=notification_data.notification_type.value,
        related_id=notification_data.related_id
    )
    
    db.add(notification)
    db.commit()
    db.refresh(notification)
    
    return notification


@router.post("/broadcast", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def broadcast_notification(
    broadcast_data: NotificationBroadcast,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    广播通知给所有用户（管理员权限）
    """
    # 获取所有活跃用户
    users = db.query(User).filter(User.is_active == True).all()
    
    count = 0
    for user in users:
        notification = Notification(
            user_id=user.id,
            title=broadcast_data.title,
            content=broadcast_data.content,
            notification_type=NotificationType.SYSTEM.value
        )
        db.add(notification)
        count += 1
    
    db.commit()
    
    return MessageResponse(message=f"已向 {count} 位用户发送通知")


@router.get("/list", response_model=NotificationListResponse)
def get_all_notifications(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回记录数"),
    user_id: Optional[int] = Query(None, description="用户ID筛选"),
    notification_type: Optional[str] = Query(None, description="通知类型筛选"),
    unread_only: bool = Query(False, description="仅显示未读通知"),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    获取所有通知（管理员权限）
    """
    query = db.query(Notification)
    
    # 用户筛选
    if user_id:
        query = query.filter(Notification.user_id == user_id)
    
    # 类型筛选
    if notification_type:
        query = query.filter(Notification.notification_type == notification_type)
    
    # 未读筛选
    if unread_only:
        query = query.filter(Notification.is_read == False)
    
    # 排序
    query = query.order_by(Notification.created_at.desc())
    
    # 获取总数
    total = query.count()
    
    # 获取未读数量
    unread_query = db.query(Notification)
    if user_id:
        unread_query = unread_query.filter(Notification.user_id == user_id)
    unread_count = unread_query.filter(Notification.is_read == False).count()
    
    # 分页
    notifications = query.offset(skip).limit(limit).all()
    
    return NotificationListResponse(
        total=total,
        unread_count=unread_count,
        notifications=notifications
    )


@router.delete("/admin/{notification_id}", response_model=MessageResponse)
def admin_delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    管理员删除通知
    """
    notification = db.query(Notification).filter(
        Notification.id == notification_id
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="通知不存在"
        )
    
    db.delete(notification)
    db.commit()
    
    return MessageResponse(message="通知删除成功")