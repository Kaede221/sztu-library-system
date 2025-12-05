"""
图书评论管理路由模块
包含评论的CRUD操作和评分功能
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from ..database import get_db, Book, User, BookReview, BorrowRecord, BorrowStatus
from ..schemas import (
    ReviewCreate,
    ReviewUpdate,
    ReviewResponse,
    ReviewWithUser,
    ReviewListResponse,
    ReviewDetailListResponse,
    MessageResponse,
)
from ..auth import get_current_active_user, get_current_admin_user

# 创建路由
router = APIRouter()


def update_book_rating(db: Session, book_id: int) -> None:
    """更新图书的平均评分和评论数量"""
    result = db.query(
        func.avg(BookReview.rating).label("avg_rating"),
        func.count(BookReview.id).label("review_count")
    ).filter(
        BookReview.book_id == book_id,
        BookReview.is_visible == True
    ).first()
    
    book = db.query(Book).filter(Book.id == book_id).first()
    if book:
        book.avg_rating = round(float(result.avg_rating or 0), 2)
        book.review_count = result.review_count or 0
        db.commit()


# ==================== 评论操作接口 ====================

@router.post("/create", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    创建图书评论
    
    - **book_id**: 图书ID
    - **rating**: 评分（1-5星）
    - **content**: 评论内容（可选）
    
    注意：只有借阅过该图书的用户才能评论
    """
    # 检查图书是否存在
    book = db.query(Book).filter(Book.id == review_data.book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="图书不存在"
        )
    
    # 检查用户是否借阅过此书
    has_borrowed = db.query(BorrowRecord).filter(
        BorrowRecord.user_id == current_user.id,
        BorrowRecord.book_id == review_data.book_id
    ).first()
    
    if not has_borrowed and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有借阅过该图书的用户才能评论"
        )
    
    # 检查用户是否已评论过此书
    existing_review = db.query(BookReview).filter(
        BookReview.user_id == current_user.id,
        BookReview.book_id == review_data.book_id
    ).first()
    
    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您已评论过此书，请勿重复评论"
        )
    
    # 创建评论
    review = BookReview(
        user_id=current_user.id,
        book_id=review_data.book_id,
        rating=review_data.rating,
        content=review_data.content,
        is_visible=True
    )
    
    db.add(review)
    db.commit()
    
    # 更新图书评分
    update_book_rating(db, review_data.book_id)
    
    db.refresh(review)
    
    return review


@router.put("/{review_id}", response_model=ReviewResponse)
def update_review(
    review_id: int,
    review_data: ReviewUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    更新评论
    
    只能更新自己的评论
    """
    review = db.query(BookReview).filter(BookReview.id == review_id).first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评论不存在"
        )
    
    # 检查权限
    if review.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此评论"
        )
    
    # 更新字段
    if review_data.rating is not None:
        review.rating = review_data.rating
    if review_data.content is not None:
        review.content = review_data.content
    
    db.commit()
    
    # 更新图书评分
    update_book_rating(db, review.book_id)
    
    db.refresh(review)
    
    return review


@router.delete("/{review_id}", response_model=MessageResponse)
def delete_review(
    review_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    删除评论
    
    只能删除自己的评论，管理员可以删除任何评论
    """
    review = db.query(BookReview).filter(BookReview.id == review_id).first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评论不存在"
        )
    
    # 检查权限
    if review.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此评论"
        )
    
    book_id = review.book_id
    
    db.delete(review)
    db.commit()
    
    # 更新图书评分
    update_book_rating(db, book_id)
    
    return MessageResponse(message="评论删除成功")


# ==================== 评论查询接口 ====================

@router.get("/book/{book_id}", response_model=ReviewDetailListResponse)
def get_book_reviews(
    book_id: int,
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回记录数"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取图书的所有评论
    """
    # 检查图书是否存在
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="图书不存在"
        )
    
    query = db.query(BookReview).options(
        joinedload(BookReview.user)
    ).filter(
        BookReview.book_id == book_id,
        BookReview.is_visible == True
    )
    
    # 排序（最新的在前）
    query = query.order_by(BookReview.created_at.desc())
    
    # 获取总数
    total = query.count()
    
    # 分页
    reviews = query.offset(skip).limit(limit).all()
    
    return ReviewDetailListResponse(total=total, reviews=reviews)


@router.get("/my-reviews", response_model=ReviewDetailListResponse)
def get_my_reviews(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回记录数"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的所有评论
    """
    query = db.query(BookReview).options(
        joinedload(BookReview.book)
    ).filter(BookReview.user_id == current_user.id)
    
    # 排序
    query = query.order_by(BookReview.created_at.desc())
    
    # 获取总数
    total = query.count()
    
    # 分页
    reviews = query.offset(skip).limit(limit).all()
    
    return ReviewDetailListResponse(total=total, reviews=reviews)


@router.get("/{review_id}", response_model=ReviewWithUser)
def get_review(
    review_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取评论详情
    """
    review = db.query(BookReview).options(
        joinedload(BookReview.user)
    ).filter(BookReview.id == review_id).first()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评论不存在"
        )
    
    # 如果评论被隐藏，只有管理员和评论者本人可以查看
    if not review.is_visible:
        if review.user_id != current_user.id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="评论不存在"
            )
    
    return review


# ==================== 管理员接口 ====================

@router.get("/list", response_model=ReviewDetailListResponse)
def get_all_reviews(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回记录数"),
    user_id: Optional[int] = Query(None, description="用户ID筛选"),
    book_id: Optional[int] = Query(None, description="图书ID筛选"),
    rating: Optional[int] = Query(None, ge=1, le=5, description="评分筛选"),
    visible_only: bool = Query(False, description="仅显示可见评论"),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    获取所有评论（管理员权限）
    """
    query = db.query(BookReview).options(
        joinedload(BookReview.user),
        joinedload(BookReview.book)
    )
    
    # 用户筛选
    if user_id:
        query = query.filter(BookReview.user_id == user_id)
    
    # 图书筛选
    if book_id:
        query = query.filter(BookReview.book_id == book_id)
    
    # 评分筛选
    if rating:
        query = query.filter(BookReview.rating == rating)
    
    # 可见性筛选
    if visible_only:
        query = query.filter(BookReview.is_visible == True)
    
    # 排序
    query = query.order_by(BookReview.created_at.desc())
    
    # 获取总数
    total = query.count()
    
    # 分页
    reviews = query.offset(skip).limit(limit).all()
    
    return ReviewDetailListResponse(total=total, reviews=reviews)


@router.post("/toggle-visibility/{review_id}", response_model=ReviewResponse)
def toggle_review_visibility(
    review_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    切换评论可见性（管理员权限）
    
    用于隐藏或显示不当评论
    """
    review = db.query(BookReview).filter(BookReview.id == review_id).first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评论不存在"
        )
    
    review.is_visible = not review.is_visible
    db.commit()
    
    # 更新图书评分
    update_book_rating(db, review.book_id)
    
    db.refresh(review)
    
    return review