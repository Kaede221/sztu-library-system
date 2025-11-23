from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import SessionLocal, Book
from ..schemas import Book as BookSchema, BookCreate, BookUpdate

# 创建路由
router = APIRouter()

# 依赖项：获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 创建图书
@router.post("/", response_model=BookSchema, status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
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

# 获取所有图书
@router.get("/", response_model=List[BookSchema])
def read_books(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    books = db.query(Book).offset(skip).limit(limit).all()
    return books

# 根据ID获取图书
@router.get("/{book_id}", response_model=BookSchema)
def read_book(book_id: int, db: Session = Depends(get_db)):
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if db_book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="图书未找到"
        )
    return db_book

# 根据图书编号获取图书
@router.get("/number/{book_number}", response_model=BookSchema)
def read_book_by_number(book_number: str, db: Session = Depends(get_db)):
    db_book = db.query(Book).filter(Book.book_number == book_number).first()
    if db_book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="图书未找到"
        )
    return db_book

# 更新图书
@router.put("/{book_id}", response_model=BookSchema)
def update_book(book_id: int, book: BookUpdate, db: Session = Depends(get_db)):
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
    update_data = book.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_book, field, value)
    
    db.commit()
    db.refresh(db_book)
    return db_book

# 删除图书
@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if db_book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="图书未找到"
        )
    
    db.delete(db_book)
    db.commit()
    return