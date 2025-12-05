"""
图书预约管理路由模块
包含预约、取消预约、预约记录查询等功能
"""

from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_

from ..database import (
    get_db, Book, User, Reservation, ReservationStatus,
    BorrowRecord, BorrowStatus, Notification, NotificationType
)
from ..schemas import (
    ReservationCreate,
    ReservationCancel,
    ReservationResponse,
    ReservationWithDetails,
    ReservationListResponse,
    ReservationDetailListResponse,
    MessageResponse,
)
from ..auth import get_current_active_user, get_current_admin_user

# 创建路由
router = APIRouter()

# 预约有效期（天）
RESERVATION_EXPIRE_DAYS = 3


def update_queue_positions(db: Session, book_id: int) -> None:
    """更新预约队列位置"""
    pending_reservations = db.query(Reservation).filter(
        Reservation.book_id == book_id,
        Reservation.status == ReservationStatus.PENDING.value
    ).order_by(Reservation.reservation_date.asc()).all()
    
    for i, reservation in enumerate(pending_reservations, 1):
        reservation.queue_position = i
    
    db.commit()


# ==================== 预约操作接口 ====================

@router.post("/create", response_model=ReservationResponse, status_code=status.HTTP_201_CREATED)
def create_reservation(
    reservation_data: ReservationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    预约图书
    
    - **book_id**: 图书ID
    
    注意：只有当图书无可借库存时才能预约
    """
    # 检查用户是否被禁用
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用，无法预约"
        )
    
    # 检查图书是否存在
    book = db.query(Book).filter(Book.id == reservation_data.book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="图书不存在"
        )
    
    # 检查图书是否有可借库存（有库存时不需要预约）
    if book.available_quantity > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该图书有可借库存，请直接借阅"
        )
    
    # 检查用户是否已预约此书
    existing_reservation = db.query(Reservation).filter(
        Reservation.user_id == current_user.id,
        Reservation.book_id == reservation_data.book_id,
        Reservation.status.in_([ReservationStatus.PENDING.value, ReservationStatus.AVAILABLE.value])
    ).first()
    
    if existing_reservation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您已预约此书，请勿重复预约"
        )
    
    # 检查用户是否已借阅此书
    existing_borrow = db.query(BorrowRecord).filter(
        BorrowRecord.user_id == current_user.id,
        BorrowRecord.book_id == reservation_data.book_id,
        BorrowRecord.status.in_([BorrowStatus.BORROWED.value, BorrowStatus.OVERDUE.value])
    ).first()
    
    if existing_borrow:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您已借阅此书，无需预约"
        )
    
    # 获取当前队列位置
    current_queue_count = db.query(Reservation).filter(
        Reservation.book_id == reservation_data.book_id,
        Reservation.status == ReservationStatus.PENDING.value
    ).count()
    
    # 创建预约记录
    reservation = Reservation(
        user_id=current_user.id,
        book_id=reservation_data.book_id,
        reservation_date=datetime.utcnow(),
        status=ReservationStatus.PENDING.value,
        queue_position=current_queue_count + 1
    )
    
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    
    return reservation


@router.post("/cancel/{reservation_id}", response_model=ReservationResponse)
def cancel_reservation(
    reservation_id: int,
    cancel_data: ReservationCancel = ReservationCancel(),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    取消预约
    
    - **reservation_id**: 预约记录ID
    - **reason**: 取消原因（可选）
    """
    # 获取预约记录
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="预约记录不存在"
        )
    
    # 检查权限
    if reservation.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作此预约记录"
        )
    
    # 检查状态
    if reservation.status not in [ReservationStatus.PENDING.value, ReservationStatus.AVAILABLE.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该预约已完成或已取消，无法操作"
        )
    
    # 如果是可取书状态，需要恢复图书可借数量
    if reservation.status == ReservationStatus.AVAILABLE.value:
        book = db.query(Book).filter(Book.id == reservation.book_id).first()
        if book:
            book.available_quantity += 1
    
    # 更新预约状态
    reservation.status = ReservationStatus.CANCELLED.value
    
    db.commit()
    
    # 更新队列位置
    update_queue_positions(db, reservation.book_id)
    
    db.refresh(reservation)
    
    return reservation


@router.post("/complete/{reservation_id}", response_model=ReservationResponse)
def complete_reservation(
    reservation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    完成预约（借阅预约的图书）
    
    当预约状态为"可取书"时，用户可以完成预约并借阅图书
    """
    # 获取预约记录
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="预约记录不存在"
        )
    
    # 检查权限
    if reservation.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作此预约记录"
        )
    
    # 检查状态
    if reservation.status != ReservationStatus.AVAILABLE.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该预约不在可取书状态"
        )
    
    # 检查是否过期
    if reservation.expire_date and datetime.utcnow() > reservation.expire_date:
        reservation.status = ReservationStatus.EXPIRED.value
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="预约已过期，请重新预约"
        )
    
    # 获取图书
    book = db.query(Book).filter(Book.id == reservation.book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="图书不存在"
        )
    
    # 创建借阅记录
    borrow_record = BorrowRecord(
        user_id=reservation.user_id,
        book_id=reservation.book_id,
        borrow_date=datetime.utcnow(),
        due_date=datetime.utcnow() + timedelta(days=30),
        status=BorrowStatus.BORROWED.value
    )
    
    # 更新图书借阅次数（可借数量在预约可取书时已经预留）
    book.borrow_count += 1
    book.available_quantity -= 1  # 扣减预留的库存
    
    # 更新预约状态
    reservation.status = ReservationStatus.COMPLETED.value
    
    db.add(borrow_record)
    db.commit()
    db.refresh(reservation)
    
    return reservation


# ==================== 预约记录查询接口 ====================

@router.get("/my-reservations", response_model=ReservationDetailListResponse)
def get_my_reservations(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回记录数"),
    status_filter: Optional[str] = Query(None, description="状态筛选"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的预约记录
    """
    query = db.query(Reservation).options(
        joinedload(Reservation.book)
    ).filter(Reservation.user_id == current_user.id)
    
    # 状态筛选
    if status_filter:
        query = query.filter(Reservation.status == status_filter)
    
    # 排序
    query = query.order_by(Reservation.created_at.desc())
    
    # 获取总数
    total = query.count()
    
    # 分页
    reservations = query.offset(skip).limit(limit).all()
    
    # 检查并更新过期状态
    for reservation in reservations:
        if (reservation.status == ReservationStatus.AVAILABLE.value and 
            reservation.expire_date and 
            datetime.utcnow() > reservation.expire_date):
            reservation.status = ReservationStatus.EXPIRED.value
    
    db.commit()
    
    return ReservationDetailListResponse(total=total, reservations=reservations)


@router.get("/active", response_model=ReservationDetailListResponse)
def get_active_reservations(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的有效预约（等待中和可取书）
    """
    reservations = db.query(Reservation).options(
        joinedload(Reservation.book)
    ).filter(
        Reservation.user_id == current_user.id,
        Reservation.status.in_([ReservationStatus.PENDING.value, ReservationStatus.AVAILABLE.value])
    ).order_by(Reservation.queue_position.asc()).all()
    
    # 检查并更新过期状态
    for reservation in reservations:
        if (reservation.status == ReservationStatus.AVAILABLE.value and 
            reservation.expire_date and 
            datetime.utcnow() > reservation.expire_date):
            reservation.status = ReservationStatus.EXPIRED.value
    
    db.commit()
    
    # 过滤掉刚刚过期的
    active_reservations = [r for r in reservations if r.status in [
        ReservationStatus.PENDING.value, ReservationStatus.AVAILABLE.value
    ]]
    
    return ReservationDetailListResponse(total=len(active_reservations), reservations=active_reservations)


# ==================== 管理员接口 ====================

@router.get("/list", response_model=ReservationDetailListResponse)
def get_all_reservations(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回记录数"),
    user_id: Optional[int] = Query(None, description="用户ID筛选"),
    book_id: Optional[int] = Query(None, description="图书ID筛选"),
    status_filter: Optional[str] = Query(None, description="状态筛选"),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    获取所有预约记录（管理员权限）
    """
    query = db.query(Reservation).options(
        joinedload(Reservation.user),
        joinedload(Reservation.book)
    )
    
    # 用户筛选
    if user_id:
        query = query.filter(Reservation.user_id == user_id)
    
    # 图书筛选
    if book_id:
        query = query.filter(Reservation.book_id == book_id)
    
    # 状态筛选
    if status_filter:
        query = query.filter(Reservation.status == status_filter)
    
    # 排序
    query = query.order_by(Reservation.created_at.desc())
    
    # 获取总数
    total = query.count()
    
    # 分页
    reservations = query.offset(skip).limit(limit).all()
    
    return ReservationDetailListResponse(total=total, reservations=reservations)


@router.get("/{reservation_id}", response_model=ReservationWithDetails)
def get_reservation(
    reservation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取预约记录详情
    """
    reservation = db.query(Reservation).options(
        joinedload(Reservation.user),
        joinedload(Reservation.book)
    ).filter(Reservation.id == reservation_id).first()
    
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="预约记录不存在"
        )
    
    # 检查权限
    if reservation.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看此预约记录"
        )
    
    return reservation


@router.get("/book/{book_id}/queue", response_model=ReservationListResponse)
def get_book_reservation_queue(
    book_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取图书的预约队列
    """
    # 检查图书是否存在
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="图书不存在"
        )
    
    reservations = db.query(Reservation).filter(
        Reservation.book_id == book_id,
        Reservation.status == ReservationStatus.PENDING.value
    ).order_by(Reservation.queue_position.asc()).all()
    
    return ReservationListResponse(total=len(reservations), reservations=reservations)


@router.post("/batch-check-expired", response_model=MessageResponse)
def batch_check_expired(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    批量检查并更新过期预约（管理员操作）
    """
    # 查找所有可取书但已过期的预约
    expired_reservations = db.query(Reservation).filter(
        Reservation.status == ReservationStatus.AVAILABLE.value,
        Reservation.expire_date < datetime.utcnow()
    ).all()
    
    count = 0
    book_ids = set()
    
    for reservation in expired_reservations:
        reservation.status = ReservationStatus.EXPIRED.value
        book_ids.add(reservation.book_id)
        
        # 恢复图书可借数量
        book = db.query(Book).filter(Book.id == reservation.book_id).first()
        if book:
            book.available_quantity += 1
        
        # 创建通知
        notification = Notification(
            user_id=reservation.user_id,
            title="预约已过期",
            content=f"您预约的图书《{book.name if book else '未知'}》已过期，请重新预约。",
            notification_type=NotificationType.SYSTEM.value,
            related_id=reservation.id
        )
        db.add(notification)
        count += 1
    
    db.commit()
    
    # 更新队列位置
    for book_id in book_ids:
        update_queue_positions(db, book_id)
    
    return MessageResponse(message=f"已处理 {count} 条过期预约")