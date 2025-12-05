"""
图书借阅管理路由模块
包含借书、还书、续借、借阅记录查询等功能
"""

from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_

from ..database import (
    get_db, Book, User, BorrowRecord, BorrowStatus,
    Reservation, ReservationStatus, Notification, NotificationType
)
from ..schemas import (
    BorrowCreate,
    BorrowReturn,
    BorrowRenew,
    BorrowRecordResponse,
    BorrowRecordWithDetails,
    BorrowRecordListResponse,
    BorrowRecordDetailListResponse,
    MessageResponse,
)
from ..auth import get_current_active_user, get_current_admin_user

# 创建路由
router = APIRouter()

# 默认借阅天数
DEFAULT_BORROW_DAYS = 30
# 最大续借次数
MAX_RENEW_COUNT = 2
# 每日逾期罚款金额
DAILY_FINE = 0.5


def calculate_fine(due_date: datetime, return_date: datetime) -> float:
    """计算逾期罚款"""
    if return_date <= due_date:
        return 0.0
    overdue_days = (return_date - due_date).days
    return round(overdue_days * DAILY_FINE, 2)


def check_and_update_overdue(db: Session, record: BorrowRecord) -> None:
    """检查并更新逾期状态"""
    if record.status == BorrowStatus.BORROWED.value and datetime.utcnow() > record.due_date:
        record.status = BorrowStatus.OVERDUE.value
        record.fine_amount = calculate_fine(record.due_date, datetime.utcnow())
        db.commit()


# ==================== 借阅操作接口 ====================

@router.post("/borrow", response_model=BorrowRecordResponse, status_code=status.HTTP_201_CREATED)
def borrow_book(
    borrow_data: BorrowCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    借阅图书
    
    - **book_id**: 图书ID
    - **borrow_days**: 借阅天数（默认30天，最长90天）
    - **user_id**: 用户ID（仅管理员可代借）
    """
    # 确定借阅用户
    if borrow_data.user_id and current_user.role == "admin":
        borrower = db.query(User).filter(User.id == borrow_data.user_id).first()
        if not borrower:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
    else:
        borrower = current_user
    
    # 检查用户是否被禁用
    if not borrower.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用，无法借阅"
        )
    
    # 检查用户当前借阅数量是否已达上限
    current_borrows = db.query(BorrowRecord).filter(
        BorrowRecord.user_id == borrower.id,
        BorrowRecord.status.in_([BorrowStatus.BORROWED.value, BorrowStatus.OVERDUE.value])
    ).count()
    
    if current_borrows >= borrower.max_borrow_count:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"已达到最大借阅数量限制（{borrower.max_borrow_count}本）"
        )
    
    # 检查用户是否有未支付的罚款
    unpaid_fines = db.query(BorrowRecord).filter(
        BorrowRecord.user_id == borrower.id,
        BorrowRecord.fine_amount > 0,
        BorrowRecord.fine_paid == False
    ).count()
    
    if unpaid_fines > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您有未支付的罚款，请先处理后再借阅"
        )
    
    # 检查图书是否存在
    book = db.query(Book).filter(Book.id == borrow_data.book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="图书不存在"
        )
    
    # 检查图书是否有可借数量
    if book.available_quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该图书暂无可借库存"
        )
    
    # 检查用户是否已借阅此书
    existing_borrow = db.query(BorrowRecord).filter(
        BorrowRecord.user_id == borrower.id,
        BorrowRecord.book_id == borrow_data.book_id,
        BorrowRecord.status.in_([BorrowStatus.BORROWED.value, BorrowStatus.OVERDUE.value])
    ).first()
    
    if existing_borrow:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您已借阅此书，请先归还后再借"
        )
    
    # 创建借阅记录
    borrow_days = borrow_data.borrow_days or DEFAULT_BORROW_DAYS
    due_date = datetime.utcnow() + timedelta(days=borrow_days)
    
    borrow_record = BorrowRecord(
        user_id=borrower.id,
        book_id=book.id,
        borrow_date=datetime.utcnow(),
        due_date=due_date,
        status=BorrowStatus.BORROWED.value
    )
    
    # 更新图书可借数量和借阅次数
    book.available_quantity -= 1
    book.borrow_count += 1
    
    db.add(borrow_record)
    db.commit()
    db.refresh(borrow_record)
    
    return borrow_record


@router.post("/return/{record_id}", response_model=BorrowRecordResponse)
def return_book(
    record_id: int,
    return_data: BorrowReturn = BorrowReturn(),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    归还图书
    
    - **record_id**: 借阅记录ID
    - **fine_paid**: 是否支付罚款（如有逾期）
    """
    # 获取借阅记录
    record = db.query(BorrowRecord).filter(BorrowRecord.id == record_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="借阅记录不存在"
        )
    
    # 检查权限（只有借阅者本人或管理员可以还书）
    if record.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作此借阅记录"
        )
    
    # 检查是否已归还
    if record.status == BorrowStatus.RETURNED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该图书已归还"
        )
    
    # 计算罚款
    return_date = datetime.utcnow()
    fine_amount = calculate_fine(record.due_date, return_date)
    
    # 更新借阅记录
    record.return_date = return_date
    record.status = BorrowStatus.RETURNED.value
    record.fine_amount = fine_amount
    record.fine_paid = return_data.fine_paid if fine_amount > 0 else True
    
    # 更新图书可借数量
    book = db.query(Book).filter(Book.id == record.book_id).first()
    if book:
        book.available_quantity += 1
    
    # 检查是否有预约此书的用户，通知第一个预约者
    pending_reservation = db.query(Reservation).filter(
        Reservation.book_id == record.book_id,
        Reservation.status == ReservationStatus.PENDING.value
    ).order_by(Reservation.queue_position.asc()).first()
    
    if pending_reservation:
        # 更新预约状态
        pending_reservation.status = ReservationStatus.AVAILABLE.value
        pending_reservation.expire_date = datetime.utcnow() + timedelta(days=3)  # 3天内取书
        pending_reservation.notified = True
        
        # 创建通知
        notification = Notification(
            user_id=pending_reservation.user_id,
            title="预约图书到馆通知",
            content=f"您预约的图书《{book.name}》已到馆，请在3天内前往借阅。",
            notification_type=NotificationType.RESERVATION_READY.value,
            related_id=pending_reservation.id
        )
        db.add(notification)
    
    db.commit()
    db.refresh(record)
    
    return record


@router.post("/renew/{record_id}", response_model=BorrowRecordResponse)
def renew_book(
    record_id: int,
    renew_data: BorrowRenew = BorrowRenew(),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    续借图书
    
    - **record_id**: 借阅记录ID
    - **renew_days**: 续借天数（默认14天，最长30天）
    """
    # 获取借阅记录
    record = db.query(BorrowRecord).filter(BorrowRecord.id == record_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="借阅记录不存在"
        )
    
    # 检查权限
    if record.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作此借阅记录"
        )
    
    # 检查是否已归还
    if record.status == BorrowStatus.RETURNED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该图书已归还，无法续借"
        )
    
    # 检查是否已逾期
    if record.status == BorrowStatus.OVERDUE.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该图书已逾期，请先归还并支付罚款"
        )
    
    # 检查续借次数
    if record.renew_count >= MAX_RENEW_COUNT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"已达到最大续借次数（{MAX_RENEW_COUNT}次）"
        )
    
    # 检查是否有人预约此书
    pending_reservations = db.query(Reservation).filter(
        Reservation.book_id == record.book_id,
        Reservation.status == ReservationStatus.PENDING.value
    ).count()
    
    if pending_reservations > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该图书有其他用户预约，无法续借"
        )
    
    # 续借
    record.due_date = record.due_date + timedelta(days=renew_data.renew_days)
    record.renew_count += 1
    
    db.commit()
    db.refresh(record)
    
    return record


# ==================== 借阅记录查询接口 ====================

@router.get("/my-records", response_model=BorrowRecordDetailListResponse)
def get_my_borrow_records(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回记录数"),
    status_filter: Optional[str] = Query(None, description="状态筛选（borrowed/returned/overdue）"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的借阅记录
    
    支持分页和状态筛选
    """
    query = db.query(BorrowRecord).options(
        joinedload(BorrowRecord.book)
    ).filter(BorrowRecord.user_id == current_user.id)
    
    # 状态筛选
    if status_filter:
        query = query.filter(BorrowRecord.status == status_filter)
    
    # 排序（最新的在前）
    query = query.order_by(BorrowRecord.created_at.desc())
    
    # 获取总数
    total = query.count()
    
    # 分页
    records = query.offset(skip).limit(limit).all()
    
    # 检查并更新逾期状态
    for record in records:
        check_and_update_overdue(db, record)
    
    return BorrowRecordDetailListResponse(total=total, records=records)


@router.get("/current", response_model=BorrowRecordDetailListResponse)
def get_current_borrows(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户正在借阅的图书
    """
    records = db.query(BorrowRecord).options(
        joinedload(BorrowRecord.book)
    ).filter(
        BorrowRecord.user_id == current_user.id,
        BorrowRecord.status.in_([BorrowStatus.BORROWED.value, BorrowStatus.OVERDUE.value])
    ).order_by(BorrowRecord.due_date.asc()).all()
    
    # 检查并更新逾期状态
    for record in records:
        check_and_update_overdue(db, record)
    
    return BorrowRecordDetailListResponse(total=len(records), records=records)


# ==================== 管理员接口 ====================

@router.get("/list", response_model=BorrowRecordDetailListResponse)
def get_all_borrow_records(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回记录数"),
    user_id: Optional[int] = Query(None, description="用户ID筛选"),
    book_id: Optional[int] = Query(None, description="图书ID筛选"),
    status_filter: Optional[str] = Query(None, description="状态筛选"),
    overdue_only: bool = Query(False, description="仅显示逾期记录"),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    获取所有借阅记录（管理员权限）
    
    支持多种筛选条件
    """
    query = db.query(BorrowRecord).options(
        joinedload(BorrowRecord.user),
        joinedload(BorrowRecord.book)
    )
    
    # 用户筛选
    if user_id:
        query = query.filter(BorrowRecord.user_id == user_id)
    
    # 图书筛选
    if book_id:
        query = query.filter(BorrowRecord.book_id == book_id)
    
    # 状态筛选
    if status_filter:
        query = query.filter(BorrowRecord.status == status_filter)
    
    # 仅逾期
    if overdue_only:
        query = query.filter(BorrowRecord.status == BorrowStatus.OVERDUE.value)
    
    # 排序
    query = query.order_by(BorrowRecord.created_at.desc())
    
    # 获取总数
    total = query.count()
    
    # 分页
    records = query.offset(skip).limit(limit).all()
    
    # 检查并更新逾期状态
    for record in records:
        check_and_update_overdue(db, record)
    
    return BorrowRecordDetailListResponse(total=total, records=records)


@router.get("/{record_id}", response_model=BorrowRecordWithDetails)
def get_borrow_record(
    record_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取借阅记录详情
    """
    record = db.query(BorrowRecord).options(
        joinedload(BorrowRecord.user),
        joinedload(BorrowRecord.book)
    ).filter(BorrowRecord.id == record_id).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="借阅记录不存在"
        )
    
    # 检查权限
    if record.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看此借阅记录"
        )
    
    check_and_update_overdue(db, record)
    
    return record


@router.post("/pay-fine/{record_id}", response_model=BorrowRecordResponse)
def pay_fine(
    record_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    支付罚款（管理员操作）
    """
    record = db.query(BorrowRecord).filter(BorrowRecord.id == record_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="借阅记录不存在"
        )
    
    if record.fine_amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该记录无需支付罚款"
        )
    
    if record.fine_paid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="罚款已支付"
        )
    
    record.fine_paid = True
    db.commit()
    db.refresh(record)
    
    return record


@router.post("/batch-check-overdue", response_model=MessageResponse)
def batch_check_overdue(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    批量检查并更新逾期状态（管理员操作）
    
    用于定时任务或手动触发
    """
    # 查找所有借阅中但已过期的记录
    overdue_records = db.query(BorrowRecord).filter(
        BorrowRecord.status == BorrowStatus.BORROWED.value,
        BorrowRecord.due_date < datetime.utcnow()
    ).all()
    
    count = 0
    for record in overdue_records:
        record.status = BorrowStatus.OVERDUE.value
        record.fine_amount = calculate_fine(record.due_date, datetime.utcnow())
        
        # 创建逾期通知
        book = db.query(Book).filter(Book.id == record.book_id).first()
        notification = Notification(
            user_id=record.user_id,
            title="图书逾期提醒",
            content=f"您借阅的图书《{book.name if book else '未知'}》已逾期，当前罚款金额：{record.fine_amount}元，请尽快归还。",
            notification_type=NotificationType.OVERDUE.value,
            related_id=record.id
        )
        db.add(notification)
        count += 1
    
    db.commit()
    
    return MessageResponse(message=f"已更新 {count} 条逾期记录")