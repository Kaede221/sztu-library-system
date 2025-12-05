"""
图书管理路由模块
包含图书的CRUD操作和搜索功能
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

from ..database import get_db, Book, User, Category, BorrowRecord, BorrowStatus
from ..schemas import (
    Book as BookSchema,
    BookCreate,
    BookUpdate,
    BookListResponse,
    BookDetailResponse,
    BookWithCategory,
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
    search: Optional[str] = Query(None, description="搜索关键词（书名、作者或图书编号）"),
    shelf_location: Optional[str] = Query(None, description="按书架位置筛选"),
    category_id: Optional[int] = Query(None, description="按分类ID筛选"),
    author: Optional[str] = Query(None, description="按作者筛选"),
    available_only: bool = Query(False, description="仅显示可借图书"),
    sort_by: str = Query("id", description="排序字段（id, name, borrow_count, avg_rating, created_at）"),
    sort_order: str = Query("desc", description="排序方向（asc, desc）"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取所有图书列表
    
    支持分页、搜索、筛选和排序
    需要登录认证
    """
    query = db.query(Book)
    
    # 搜索过滤（书名、作者、图书编号、ISBN）
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Book.name.like(search_pattern),
                Book.book_number.like(search_pattern),
                Book.author.like(search_pattern),
                Book.isbn.like(search_pattern)
            )
        )
    
    # 书架位置过滤
    if shelf_location:
        query = query.filter(Book.shelf_location == shelf_location)
    
    # 分类过滤
    if category_id:
        query = query.filter(Book.category_id == category_id)
    
    # 作者过滤
    if author:
        query = query.filter(Book.author.like(f"%{author}%"))
    
    # 仅显示可借图书
    if available_only:
        query = query.filter(Book.available_quantity > 0)
    
    # 排序
    sort_column = getattr(Book, sort_by, Book.id)
    if sort_order.lower() == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())
    
    # 获取总数
    total = query.count()
    
    # 分页
    books = query.offset(skip).limit(limit).all()
    
    return BookListResponse(total=total, books=books)


@router.get("/detail/{book_id}", response_model=BookDetailResponse)
def get_book_detail(
    book_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取图书详情（包含分类信息）
    
    需要登录认证
    """
    db_book = db.query(Book).options(joinedload(Book.category)).filter(Book.id == book_id).first()
    if db_book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="图书未找到"
        )
    return db_book


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


@router.get("/isbn/{isbn}", response_model=BookSchema)
def get_book_by_isbn(
    isbn: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    根据ISBN获取图书信息
    
    需要登录认证
    """
    db_book = db.query(Book).filter(Book.isbn == isbn).first()
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
    - **author**: 作者（可选）
    - **isbn**: ISBN（可选，唯一）
    - **publisher**: 出版社（可选）
    - **publish_date**: 出版日期（可选）
    - **price**: 价格（可选）
    - **description**: 图书简介（可选）
    - **category_id**: 分类ID（可选）
    - **tags**: 标签（可选）
    """
    # 检查图书编号是否已存在
    db_book = db.query(Book).filter(Book.book_number == book.book_number).first()
    if db_book:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="图书编号已存在"
        )
    
    # 检查ISBN是否已存在（如果提供了ISBN）
    if book.isbn:
        existing_isbn = db.query(Book).filter(Book.isbn == book.isbn).first()
        if existing_isbn:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ISBN已存在"
            )
    
    # 检查分类是否存在（如果提供了分类ID）
    if book.category_id:
        category = db.query(Category).filter(Category.id == book.category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="分类不存在"
            )
    
    # 检查数量是否为负数
    if book.quantity < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="图书数量不能为负数"
        )
    
    # 设置可借数量
    available_quantity = book.available_quantity if book.available_quantity is not None else book.quantity
    
    # 创建新图书
    db_book = Book(
        name=book.name,
        preview_image=book.preview_image,
        book_number=book.book_number,
        shelf_location=book.shelf_location,
        quantity=book.quantity,
        available_quantity=available_quantity,
        author=book.author,
        isbn=book.isbn,
        publisher=book.publisher,
        publish_date=book.publish_date,
        price=book.price,
        description=book.description,
        category_id=book.category_id,
        tags=book.tags
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
    
    可更新所有图书字段
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
    
    # 如果提供了ISBN，检查是否与其他图书冲突
    if book.isbn and book.isbn != db_book.isbn:
        existing_isbn = db.query(Book).filter(Book.isbn == book.isbn).first()
        if existing_isbn:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ISBN已存在"
            )
    
    # 检查分类是否存在（如果提供了分类ID）
    if book.category_id:
        category = db.query(Category).filter(Category.id == book.category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="分类不存在"
            )
    
    # 如果提供了数量，检查是否为负数
    if book.quantity is not None and book.quantity < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="图书数量不能为负数"
        )
    
    if book.available_quantity is not None and book.available_quantity < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="可借数量不能为负数"
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
    
    注意：如果图书有未归还的借阅记录，则不能删除
    """
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if db_book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="图书未找到"
        )
    
    # 检查是否有未归还的借阅记录
    active_borrows = db.query(BorrowRecord).filter(
        BorrowRecord.book_id == book_id,
        BorrowRecord.status == BorrowStatus.BORROWED.value
    ).count()
    
    if active_borrows > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"该图书有 {active_borrows} 本未归还，无法删除"
        )
    
    db.delete(db_book)
    db.commit()
    
    return MessageResponse(message="图书删除成功")


# ==================== 图书标签接口 ====================

@router.get("/tags/all", response_model=List[str])
def get_all_tags(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取所有图书标签
    
    返回去重后的标签列表
    """
    books = db.query(Book.tags).filter(Book.tags.isnot(None)).all()
    tags_set = set()
    for book in books:
        if book.tags:
            for tag in book.tags.split(","):
                tag = tag.strip()
                if tag:
                    tags_set.add(tag)
    return sorted(list(tags_set))