"""
图书分类管理路由模块
包含分类的CRUD操作和树形结构查询
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ..database import get_db, Category, Book, User
from ..schemas import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryListResponse,
    CategoryTreeResponse,
    CategoryWithChildren,
    MessageResponse,
)
from ..auth import get_current_active_user, get_current_admin_user

# 创建路由
router = APIRouter()


# ==================== 分类查询接口 ====================

@router.get("/list", response_model=CategoryListResponse)
def get_all_categories(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=500, description="返回记录数"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    parent_id: Optional[int] = Query(None, description="父分类ID（传0获取顶级分类）"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取分类列表
    
    支持分页和搜索
    需要登录认证
    """
    query = db.query(Category)
    
    # 搜索过滤
    if search:
        query = query.filter(Category.name.like(f"%{search}%"))
    
    # 父分类过滤
    if parent_id is not None:
        if parent_id == 0:
            query = query.filter(Category.parent_id.is_(None))
        else:
            query = query.filter(Category.parent_id == parent_id)
    
    # 排序
    query = query.order_by(Category.sort_order.asc(), Category.id.asc())
    
    # 获取总数
    total = query.count()
    
    # 分页
    categories = query.offset(skip).limit(limit).all()
    
    return CategoryListResponse(total=total, categories=categories)


def build_category_tree(categories: List[Category], parent_id: Optional[int] = None) -> List[CategoryWithChildren]:
    """递归构建分类树"""
    tree = []
    for category in categories:
        if category.parent_id == parent_id:
            children = build_category_tree(categories, category.id)
            category_dict = CategoryWithChildren(
                id=category.id,
                name=category.name,
                description=category.description,
                parent_id=category.parent_id,
                sort_order=category.sort_order,
                created_at=category.created_at,
                children=children
            )
            tree.append(category_dict)
    return tree


@router.get("/tree", response_model=CategoryTreeResponse)
def get_category_tree(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取分类树形结构
    
    返回完整的分类层级结构
    需要登录认证
    """
    categories = db.query(Category).order_by(Category.sort_order.asc(), Category.id.asc()).all()
    tree = build_category_tree(categories)
    return CategoryTreeResponse(categories=tree)


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    根据ID获取分类信息
    
    需要登录认证
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类未找到"
        )
    return category


@router.get("/{category_id}/children", response_model=CategoryListResponse)
def get_category_children(
    category_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取指定分类的子分类
    
    需要登录认证
    """
    # 检查分类是否存在
    category = db.query(Category).filter(Category.id == category_id).first()
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类未找到"
        )
    
    children = db.query(Category).filter(
        Category.parent_id == category_id
    ).order_by(Category.sort_order.asc(), Category.id.asc()).all()
    
    return CategoryListResponse(total=len(children), categories=children)


# ==================== 分类管理接口（管理员权限） ====================

@router.post("/create", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category: CategoryCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    创建新分类（管理员权限）
    
    - **name**: 分类名称（唯一）
    - **description**: 分类描述（可选）
    - **parent_id**: 父分类ID（可选，不填则为顶级分类）
    - **sort_order**: 排序顺序（可选，默认0）
    """
    # 检查分类名称是否已存在
    existing = db.query(Category).filter(Category.name == category.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="分类名称已存在"
        )
    
    # 检查父分类是否存在
    if category.parent_id:
        parent = db.query(Category).filter(Category.id == category.parent_id).first()
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="父分类不存在"
            )
    
    # 创建新分类
    db_category = Category(
        name=category.name,
        description=category.description,
        parent_id=category.parent_id,
        sort_order=category.sort_order
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category: CategoryUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    更新分类信息（管理员权限）
    
    可更新字段：
    - **name**: 分类名称
    - **description**: 分类描述
    - **parent_id**: 父分类ID
    - **sort_order**: 排序顺序
    """
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if db_category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类未找到"
        )
    
    # 如果提供了名称，检查是否与其他分类冲突
    if category.name and category.name != db_category.name:
        existing = db.query(Category).filter(Category.name == category.name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="分类名称已存在"
            )
    
    # 如果提供了父分类ID，检查是否存在且不能是自己或自己的子分类
    if category.parent_id is not None:
        if category.parent_id == category_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能将分类设为自己的子分类"
            )
        
        if category.parent_id != 0:
            parent = db.query(Category).filter(Category.id == category.parent_id).first()
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="父分类不存在"
                )
            
            # 检查是否会形成循环引用
            current_parent = parent
            while current_parent:
                if current_parent.id == category_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="不能将分类设为其子分类的子分类（循环引用）"
                    )
                current_parent = db.query(Category).filter(
                    Category.id == current_parent.parent_id
                ).first() if current_parent.parent_id else None
    
    # 更新字段
    update_data = category.model_dump(exclude_unset=True)
    
    # 处理 parent_id 为 0 的情况（设为顶级分类）
    if "parent_id" in update_data and update_data["parent_id"] == 0:
        update_data["parent_id"] = None
    
    for field, value in update_data.items():
        setattr(db_category, field, value)
    
    db.commit()
    db.refresh(db_category)
    return db_category


@router.delete("/{category_id}", response_model=MessageResponse)
def delete_category(
    category_id: int,
    force: bool = Query(False, description="是否强制删除（包括子分类）"),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    删除分类（管理员权限）
    
    - 如果分类下有图书，则不能删除
    - 如果分类下有子分类，需要设置 force=true 强制删除
    """
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if db_category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类未找到"
        )
    
    # 检查是否有图书使用此分类
    book_count = db.query(Book).filter(Book.category_id == category_id).count()
    if book_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"该分类下有 {book_count} 本图书，无法删除。请先移除或更改这些图书的分类。"
        )
    
    # 检查是否有子分类
    children_count = db.query(Category).filter(Category.parent_id == category_id).count()
    if children_count > 0:
        if not force:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"该分类下有 {children_count} 个子分类，请设置 force=true 强制删除"
            )
        
        # 递归删除子分类
        def delete_children(parent_id: int):
            children = db.query(Category).filter(Category.parent_id == parent_id).all()
            for child in children:
                # 检查子分类下是否有图书
                child_book_count = db.query(Book).filter(Book.category_id == child.id).count()
                if child_book_count > 0:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"子分类 '{child.name}' 下有 {child_book_count} 本图书，无法删除"
                    )
                delete_children(child.id)
                db.delete(child)
        
        delete_children(category_id)
    
    db.delete(db_category)
    db.commit()
    
    return MessageResponse(message="分类删除成功")


# ==================== 批量操作接口 ====================

@router.post("/batch-create", response_model=List[CategoryResponse], status_code=status.HTTP_201_CREATED)
def batch_create_categories(
    categories: List[CategoryCreate],
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    批量创建分类（管理员权限）
    
    用于初始化分类数据
    """
    created_categories = []
    
    for category in categories:
        # 检查分类名称是否已存在
        existing = db.query(Category).filter(Category.name == category.name).first()
        if existing:
            continue  # 跳过已存在的分类
        
        # 检查父分类是否存在
        if category.parent_id:
            parent = db.query(Category).filter(Category.id == category.parent_id).first()
            if not parent:
                continue  # 跳过父分类不存在的
        
        db_category = Category(
            name=category.name,
            description=category.description,
            parent_id=category.parent_id,
            sort_order=category.sort_order
        )
        db.add(db_category)
        db.flush()  # 获取ID但不提交
        created_categories.append(db_category)
    
    db.commit()
    
    # 刷新所有创建的分类
    for cat in created_categories:
        db.refresh(cat)
    
    return created_categories