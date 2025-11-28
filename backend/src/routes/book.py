"""
图书管理路由模块
包含图书的CRUD操作和搜索功能
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ..database import get_db, Book, User
from ..schemas import (
    Book as BookSchema,
    BookCreate,
    BookUpdate,
    BookListResponse,
    MessageResponse,
)
from ..auth import get_current_active_user, get_current_admin_user

# 创建路由
router = APIRouter()


# ==================== 图书查询接口 ====================

@router.get("/list", response_model=BookListResponse)
def get_all_books(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回记录数"),
    search: Optional[str] = Query(None, description="搜索关键词（书名或图书编号）"),
    shelf_location: Optional[str] = Query(None, description="按书架位置筛选"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取所有图书列表
    
    支持分页、搜索和筛选
    需要登录认证
    """
    query = db.query(Book)
    
    # 搜索过滤
    if search:
        query = query.filter(
            (Book.name.contains(search)) | (Book.book_number.contains(search))
        )
    
    # 书架位置过滤
    if shelf_location:
        query = query.filter(Book.shelf_location == shelf_location)
    
    # 获取总数
    total = query.count()
    
    # 分页
    books = query.offset(skip).limit(limit).all()
    
    return BookListResponse(total=total, books=books)


@router.get("/{book_id}", response_model=BookSchema)
def get_book(
    book_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    根据ID获取图书信息
    
    需要登录认证
    """
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if db_book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="图书未找到"
        )
    return db_book


@router.get("/number/{book_number}", response_model=BookSchema)
def get_book_by_number(
    book_number: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    根据图书编号获取图书信息
    
    需要登录认证
    """
    db_book = db.query(Book).filter(Book.book_number == book_number).first()
    if db_book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="图书未找到"
        )
    return db_book


# ==================== 图书管理接口（管理员权限） ====================

@router.post("/create", response_model=BookSchema, status_code=status.HTTP_201_CREATED)
def create_book(
    book: BookCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    创建新图书（管理员权限）
    
    - **name**: 图书名称
    - **book_number**: 图书编号（唯一）
    - **shelf_location**: 书架位置
    - **quantity**: 数量
    - **preview_image**: 预览图片URL（可选）
    """
    # 检查图书编号是否已存在
    db_book = db.query(Book).filter(Book.book_number == book.book_number).first()
    if db_book:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="图书编号已存在"
        )
    
    # 检查数量是否为负数
    if book.quantity < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="图书数量不能为负数"
        )
    
    # 创建新图书
    db_book = Book(
        name=book.name,
        preview_image=book.preview_image,
        book_number=book.book_number,
        shelf_location=book.shelf_location,
        quantity=book.quantity
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


@router.put("/{book_id}", response_model=BookSchema)
def update_book(
    book_id: int,
    book: BookUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    更新图书信息（管理员权限）
    
    可更新字段：
    - **name**: 图书名称
    - **book_number**: 图书编号
    - **shelf_location**: 书架位置
    - **quantity**: 数量
    - **preview_image**: 预览图片URL
    """
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if db_book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="图书未找到"
        )
    
    # 如果提供了图书编号，检查是否与其他图书冲突
    if book.book_number and book.book_number != db_book.book_number:
        existing_book = db.query(Book).filter(Book.book_number == book.book_number).first()
        if existing_book:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="图书编号已存在"
            )
    
    # 如果提供了数量，检查是否为负数
    if book.quantity is not None and book.quantity < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="图书数量不能为负数"
        )
    
    # 更新字段
    update_data = book.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_book, field, value)
    
    db.commit()
    db.refresh(db_book)
    return db_book


@router.delete("/{book_id}", response_model=MessageResponse)
def delete_book(
    book_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    删除图书（管理员权限）
    """
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if db_book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="图书未找到"
        )
    
    db.delete(db_book)
    db.commit()
    
    return MessageResponse(message="图书删除成功")