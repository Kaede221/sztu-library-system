"""
图书收藏管理路由模块
包含收藏的添加、删除和查询功能
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload

from ..database import get_db, Book, User, Favorite
from ..schemas import (
    FavoriteCreate,
    FavoriteResponse,
    FavoriteWithBook,
    FavoriteListResponse,
    FavoriteDetailListResponse,
    MessageResponse,
)
from ..auth import get_current_active_user, get_current_admin_user

# 创建路由
router = APIRouter()


# ==================== 收藏操作接口 ====================

@router.post("/add", response_model=FavoriteResponse, status_code=status.HTTP_201_CREATED)
def add_favorite(
    favorite_data: FavoriteCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    添加收藏
    
    - **book_id**: 图书ID
    """
    # 检查图书是否存在
    book = db.query(Book).filter(Book.id == favorite_data.book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="图书不存在"
        )
    
    # 检查是否已收藏
    existing_favorite = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.book_id == favorite_data.book_id
    ).first()
    
    if existing_favorite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您已收藏此书"
        )
    
    # 创建收藏
    favorite = Favorite(
        user_id=current_user.id,
        book_id=favorite_data.book_id
    )
    
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    
    return favorite


@router.delete("/remove/{book_id}", response_model=MessageResponse)
def remove_favorite(
    book_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    取消收藏
    
    - **book_id**: 图书ID
    """
    favorite = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.book_id == book_id
    ).first()
    
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到收藏记录"
        )
    
    db.delete(favorite)
    db.commit()
    
    return MessageResponse(message="取消收藏成功")


@router.delete("/{favorite_id}", response_model=MessageResponse)
def delete_favorite(
    favorite_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    删除收藏（通过收藏ID）
    """
    favorite = db.query(Favorite).filter(Favorite.id == favorite_id).first()
    
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="收藏记录不存在"
        )
    
    # 检查权限
    if favorite.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此收藏"
        )
    
    db.delete(favorite)
    db.commit()
    
    return MessageResponse(message="删除收藏成功")


# ==================== 收藏查询接口 ====================

@router.get("/my-favorites", response_model=FavoriteDetailListResponse)
def get_my_favorites(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回记录数"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的收藏列表
    """
    query = db.query(Favorite).options(
        joinedload(Favorite.book)
    ).filter(Favorite.user_id == current_user.id)
    
    # 排序（最新的在前）
    query = query.order_by(Favorite.created_at.desc())
    
    # 获取总数
    total = query.count()
    
    # 分页
    favorites = query.offset(skip).limit(limit).all()
    
    return FavoriteDetailListResponse(total=total, favorites=favorites)


@router.get("/check/{book_id}")
def check_favorite(
    book_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    检查是否已收藏某本书
    """
    favorite = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.book_id == book_id
    ).first()
    
    return {
        "is_favorited": favorite is not None,
        "favorite_id": favorite.id if favorite else None
    }


@router.get("/book/{book_id}/count")
def get_book_favorite_count(
    book_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取图书的收藏数量
    """
    # 检查图书是否存在
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="图书不存在"
        )
    
    count = db.query(Favorite).filter(Favorite.book_id == book_id).count()
    
    return {
        "book_id": book_id,
        "favorite_count": count
    }


# ==================== 管理员接口 ====================

@router.get("/list", response_model=FavoriteDetailListResponse)
def get_all_favorites(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回记录数"),
    user_id: Optional[int] = Query(None, description="用户ID筛选"),
    book_id: Optional[int] = Query(None, description="图书ID筛选"),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    获取所有收藏记录（管理员权限）
    """
    query = db.query(Favorite).options(
        joinedload(Favorite.user),
        joinedload(Favorite.book)
    )
    
    # 用户筛选
    if user_id:
        query = query.filter(Favorite.user_id == user_id)
    
    # 图书筛选
    if book_id:
        query = query.filter(Favorite.book_id == book_id)
    
    # 排序
    query = query.order_by(Favorite.created_at.desc())
    
    # 获取总数
    total = query.count()
    
    # 分页
    favorites = query.offset(skip).limit(limit).all()
    
    return FavoriteDetailListResponse(total=total, favorites=favorites)


@router.get("/stats/popular-books")
def get_popular_books_by_favorites(
    limit: int = Query(10, ge=1, le=50, description="返回数量"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取收藏最多的图书
    """
    from sqlalchemy import func
    
    results = db.query(
        Book.id,
        Book.name,
        Book.author,
        Book.preview_image,
        func.count(Favorite.id).label("favorite_count")
    ).join(
        Favorite, Favorite.book_id == Book.id
    ).group_by(
        Book.id
    ).order_by(
        func.count(Favorite.id).desc()
    ).limit(limit).all()
    
    return {
        "popular_books": [
            {
                "book_id": r.id,
                "book_name": r.name,
                "author": r.author,
                "preview_image": r.preview_image,
                "favorite_count": r.favorite_count
            }
            for r in results
        ]
    }