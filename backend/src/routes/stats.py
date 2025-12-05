"""
统计分析路由模块
包含各种统计数据和报表功能
"""

from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, and_

from ..database import (
    get_db, User, Book, Category, BorrowRecord, BorrowStatus,
    Reservation, ReservationStatus, BookReview, Favorite
)
from ..schemas import (
    DashboardStats,
    BookRankingItem,
    BookRankingResponse,
    UserBorrowStats,
    MonthlyStats,
    MonthlyStatsResponse,
    CategoryStats,
    CategoryStatsResponse,
)
from ..auth import get_current_active_user, get_current_admin_user

# 创建路由
router = APIRouter()


# ==================== 仪表盘统计 ====================

@router.get("/dashboard", response_model=DashboardStats)
def get_dashboard_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取仪表盘统计数据
    """
    # 用户统计
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    
    # 图书统计
    total_books = db.query(Book).count()
    total_categories = db.query(Category).count()
    
    # 借阅统计
    total_borrow_records = db.query(BorrowRecord).count()
    active_borrows = db.query(BorrowRecord).filter(
        BorrowRecord.status == BorrowStatus.BORROWED.value
    ).count()
    overdue_borrows = db.query(BorrowRecord).filter(
        BorrowRecord.status == BorrowStatus.OVERDUE.value
    ).count()
    
    # 预约统计
    total_reservations = db.query(Reservation).count()
    pending_reservations = db.query(Reservation).filter(
        Reservation.status == ReservationStatus.PENDING.value
    ).count()
    
    return DashboardStats(
        total_users=total_users,
        total_books=total_books,
        total_categories=total_categories,
        active_users=active_users,
        total_borrow_records=total_borrow_records,
        active_borrows=active_borrows,
        overdue_borrows=overdue_borrows,
        total_reservations=total_reservations,
        pending_reservations=pending_reservations
    )


# ==================== 图书排行榜 ====================

@router.get("/book-ranking/borrow", response_model=BookRankingResponse)
def get_borrow_ranking(
    limit: int = Query(10, ge=1, le=50, description="返回数量"),
    days: Optional[int] = Query(None, description="统计天数（不填则统计全部）"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取借阅排行榜
    """
    query = db.query(
        Book.id,
        Book.name,
        Book.author,
        Book.borrow_count,
        Book.avg_rating
    )
    
    if days:
        # 统计指定天数内的借阅
        start_date = datetime.utcnow() - timedelta(days=days)
        subquery = db.query(
            BorrowRecord.book_id,
            func.count(BorrowRecord.id).label("recent_borrow_count")
        ).filter(
            BorrowRecord.borrow_date >= start_date
        ).group_by(BorrowRecord.book_id).subquery()
        
        query = db.query(
            Book.id,
            Book.name,
            Book.author,
            func.coalesce(subquery.c.recent_borrow_count, 0).label("borrow_count"),
            Book.avg_rating
        ).outerjoin(
            subquery, Book.id == subquery.c.book_id
        ).order_by(
            func.coalesce(subquery.c.recent_borrow_count, 0).desc()
        )
    else:
        query = query.order_by(Book.borrow_count.desc())
    
    results = query.limit(limit).all()
    
    rankings = [
        BookRankingItem(
            book_id=r.id,
            book_name=r.name,
            author=r.author,
            borrow_count=r.borrow_count or 0,
            avg_rating=float(r.avg_rating or 0)
        )
        for r in results
    ]
    
    return BookRankingResponse(rankings=rankings)


@router.get("/book-ranking/rating", response_model=BookRankingResponse)
def get_rating_ranking(
    limit: int = Query(10, ge=1, le=50, description="返回数量"),
    min_reviews: int = Query(1, ge=1, description="最少评论数"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取评分排行榜
    """
    results = db.query(
        Book.id,
        Book.name,
        Book.author,
        Book.borrow_count,
        Book.avg_rating
    ).filter(
        Book.review_count >= min_reviews
    ).order_by(
        Book.avg_rating.desc()
    ).limit(limit).all()
    
    rankings = [
        BookRankingItem(
            book_id=r.id,
            book_name=r.name,
            author=r.author,
            borrow_count=r.borrow_count or 0,
            avg_rating=float(r.avg_rating or 0)
        )
        for r in results
    ]
    
    return BookRankingResponse(rankings=rankings)


# ==================== 用户借阅统计 ====================

@router.get("/user-borrow-stats")
def get_user_borrow_stats(
    user_id: Optional[int] = Query(None, description="用户ID（不填则返回当前用户）"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取用户借阅统计
    """
    target_user_id = user_id if user_id and current_user.role == "admin" else current_user.id
    
    # 获取用户信息
    user = db.query(User).filter(User.id == target_user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 总借阅数
    total_borrows = db.query(BorrowRecord).filter(
        BorrowRecord.user_id == target_user_id
    ).count()
    
    # 当前借阅数
    current_borrows = db.query(BorrowRecord).filter(
        BorrowRecord.user_id == target_user_id,
        BorrowRecord.status.in_([BorrowStatus.BORROWED.value, BorrowStatus.OVERDUE.value])
    ).count()
    
    # 逾期次数
    overdue_count = db.query(BorrowRecord).filter(
        BorrowRecord.user_id == target_user_id,
        BorrowRecord.status == BorrowStatus.OVERDUE.value
    ).count()
    
    # 总罚款
    total_fines = db.query(func.sum(BorrowRecord.fine_amount)).filter(
        BorrowRecord.user_id == target_user_id
    ).scalar() or 0
    
    # 未支付罚款
    unpaid_fines = db.query(func.sum(BorrowRecord.fine_amount)).filter(
        BorrowRecord.user_id == target_user_id,
        BorrowRecord.fine_paid == False,
        BorrowRecord.fine_amount > 0
    ).scalar() or 0
    
    return {
        "user_id": target_user_id,
        "username": user.username,
        "total_borrows": total_borrows,
        "current_borrows": current_borrows,
        "overdue_count": overdue_count,
        "total_fines": float(total_fines),
        "unpaid_fines": float(unpaid_fines),
        "max_borrow_count": user.max_borrow_count
    }


# ==================== 月度统计 ====================

@router.get("/monthly", response_model=MonthlyStatsResponse)
def get_monthly_stats(
    months: int = Query(12, ge=1, le=24, description="统计月数"),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    获取月度统计数据（管理员权限）
    """
    stats = []
    
    for i in range(months):
        # 计算月份范围
        end_date = datetime.utcnow().replace(day=1) - timedelta(days=i*30)
        start_date = end_date.replace(day=1)
        if end_date.month == 12:
            next_month = end_date.replace(year=end_date.year + 1, month=1, day=1)
        else:
            next_month = end_date.replace(month=end_date.month + 1, day=1)
        
        month_str = start_date.strftime("%Y-%m")
        
        # 借阅数
        borrow_count = db.query(BorrowRecord).filter(
            BorrowRecord.borrow_date >= start_date,
            BorrowRecord.borrow_date < next_month
        ).count()
        
        # 归还数
        return_count = db.query(BorrowRecord).filter(
            BorrowRecord.return_date >= start_date,
            BorrowRecord.return_date < next_month
        ).count()
        
        # 新用户数
        new_users = db.query(User).filter(
            User.created_at >= start_date,
            User.created_at < next_month
        ).count()
        
        # 新图书数
        new_books = db.query(Book).filter(
            Book.created_at >= start_date,
            Book.created_at < next_month
        ).count()
        
        stats.append(MonthlyStats(
            month=month_str,
            borrow_count=borrow_count,
            return_count=return_count,
            new_users=new_users,
            new_books=new_books
        ))
    
    # 反转顺序，最早的月份在前
    stats.reverse()
    
    return MonthlyStatsResponse(stats=stats)


# ==================== 分类统计 ====================

@router.get("/category", response_model=CategoryStatsResponse)
def get_category_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取分类统计数据
    """
    # 获取每个分类的图书数量和借阅数量
    results = db.query(
        Category.id,
        Category.name,
        func.count(Book.id).label("book_count"),
        func.coalesce(func.sum(Book.borrow_count), 0).label("borrow_count")
    ).outerjoin(
        Book, Book.category_id == Category.id
    ).group_by(
        Category.id
    ).order_by(
        func.count(Book.id).desc()
    ).all()
    
    stats = [
        CategoryStats(
            category_id=r.id,
            category_name=r.name,
            book_count=r.book_count or 0,
            borrow_count=int(r.borrow_count or 0)
        )
        for r in results
    ]
    
    return CategoryStatsResponse(stats=stats)


# ==================== 其他统计 ====================

@router.get("/overview")
def get_overview(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    获取系统概览（管理员权限）
    """
    # 今日统计
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    today_borrows = db.query(BorrowRecord).filter(
        BorrowRecord.borrow_date >= today
    ).count()
    
    today_returns = db.query(BorrowRecord).filter(
        BorrowRecord.return_date >= today
    ).count()
    
    today_new_users = db.query(User).filter(
        User.created_at >= today
    ).count()
    
    # 本周统计
    week_start = today - timedelta(days=today.weekday())
    
    week_borrows = db.query(BorrowRecord).filter(
        BorrowRecord.borrow_date >= week_start
    ).count()
    
    week_returns = db.query(BorrowRecord).filter(
        BorrowRecord.return_date >= week_start
    ).count()
    
    # 库存统计
    total_quantity = db.query(func.sum(Book.quantity)).scalar() or 0
    available_quantity = db.query(func.sum(Book.available_quantity)).scalar() or 0
    
    # 评论统计
    total_reviews = db.query(BookReview).count()
    avg_rating = db.query(func.avg(BookReview.rating)).scalar() or 0
    
    # 收藏统计
    total_favorites = db.query(Favorite).count()
    
    return {
        "today": {
            "borrows": today_borrows,
            "returns": today_returns,
            "new_users": today_new_users
        },
        "this_week": {
            "borrows": week_borrows,
            "returns": week_returns
        },
        "inventory": {
            "total_quantity": int(total_quantity),
            "available_quantity": int(available_quantity),
            "borrowed_quantity": int(total_quantity) - int(available_quantity)
        },
        "reviews": {
            "total": total_reviews,
            "avg_rating": round(float(avg_rating), 2)
        },
        "favorites": {
            "total": total_favorites
        }
    }


@router.get("/top-borrowers")
def get_top_borrowers(
    limit: int = Query(10, ge=1, le=50, description="返回数量"),
    days: Optional[int] = Query(30, description="统计天数"),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    获取借阅最多的用户（管理员权限）
    """
    query = db.query(
        User.id,
        User.username,
        User.full_name,
        func.count(BorrowRecord.id).label("borrow_count")
    ).join(
        BorrowRecord, BorrowRecord.user_id == User.id
    )
    
    if days:
        start_date = datetime.utcnow() - timedelta(days=days)
        query = query.filter(BorrowRecord.borrow_date >= start_date)
    
    results = query.group_by(
        User.id
    ).order_by(
        func.count(BorrowRecord.id).desc()
    ).limit(limit).all()
    
    return {
        "top_borrowers": [
            {
                "user_id": r.id,
                "username": r.username,
                "full_name": r.full_name,
                "borrow_count": r.borrow_count
            }
            for r in results
        ]
    }