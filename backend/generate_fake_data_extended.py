import sqlite3
import random
from datetime import datetime, timedelta

def generate_users(n=20):
    """生成n个假用户"""
    users = []
    for i in range(1, n+1):
        username = f"user{i}"
        email = f"user{i}@example.com"
        hashed_password = "$5$rounds=535000$8HpUeJH60RaZ0Jqu$qifrXfRo34JS7RdODh7aEp9onrSg9AInOa8N.FB7Fb3"  # 与admin相同哈希
        full_name = f"用户{i}"
        role = "user"
        is_active = True
        max_borrow_count = random.choice([3,5,10])
        created_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")
        updated_at = created_at
        users.append((username, email, hashed_password, full_name, role, is_active, max_borrow_count, created_at, updated_at))
    return users

def generate_books(n=20):
    """生成n本假图书"""
    books = []
    categories = [1]  # 现有分类ID
    for i in range(1, n+1):
        name = f"图书{i}"
        preview_image = ""
        book_number = f"BK{1000+i:04d}"
        shelf_location = f"S{random.randint(1,10)}-{random.randint(1,50)}"
        quantity = random.randint(1, 10)
        available_quantity = quantity - random.randint(0, 2)
        if available_quantity < 0:
            available_quantity = 0
        author = f"作者{random.randint(1, 10)}"
        isbn = f"978-3-{random.randint(1000,9999)}-{random.randint(1000,9999)}-{random.randint(0,9)}"
        publisher = random.choice(["人民出版社", "清华大学出版社", "机械工业出版社", "电子工业出版社", "上海文艺出版社"])
        publish_date = f"{random.randint(2000,2023)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        price = round(random.uniform(20.0, 150.0), 2)
        description = f"这是图书{i}的简介，内容非常精彩。"
        category_id = random.choice(categories)
        tags = "小说,文学" if i % 2 == 0 else "科技,编程"
        borrow_count = random.randint(0, 50)
        avg_rating = round(random.uniform(3.0, 5.0), 1)
        review_count = random.randint(0, 20)
        created_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")
        updated_at = created_at
        books.append((name, preview_image, book_number, shelf_location, quantity, available_quantity,
                     author, isbn, publisher, publish_date, price, description, category_id, tags,
                     borrow_count, avg_rating, review_count, created_at, updated_at))
    return books

def generate_borrow_records(user_ids, book_ids, n_per_user=2):
    """为每个用户生成借阅记录"""
    records = []
    statuses = ["borrowed", "returned", "overdue"]
    for user_id in user_ids:
        # 每个用户随机借阅几本书
        num = random.randint(0, n_per_user)
        chosen_books = random.sample(book_ids, min(num, len(book_ids)))
        for book_id in chosen_books:
            borrow_date = datetime.utcnow() - timedelta(days=random.randint(1, 60))
            due_date = borrow_date + timedelta(days=14)
            return_date = None
            status = random.choice(statuses)
            if status == "returned":
                return_date = borrow_date + timedelta(days=random.randint(1, 14))
            elif status == "overdue":
                return_date = None
            else:
                return_date = None
            renew_count = random.randint(0, 2)
            fine_amount = 0.0 if status != "overdue" else round(random.uniform(5.0, 30.0), 2)
            fine_paid = fine_amount == 0.0 or random.choice([True, False])
            created_at = borrow_date.strftime("%Y-%m-%d %H:%M:%S.%f")
            records.append((user_id, book_id, borrow_date.strftime("%Y-%m-%d %H:%M:%S.%f"),
                           due_date.strftime("%Y-%m-%d %H:%M:%S.%f"),
                           return_date.strftime("%Y-%m-%d %H:%M:%S.%f") if return_date else None,
                           status, renew_count, fine_amount, fine_paid, created_at))
    return records

def generate_reviews(user_ids, book_ids, n=30):
    """生成评论"""
    reviews = []
    for _ in range(n):
        user_id = random.choice(user_ids)
        book_id = random.choice(book_ids)
        rating = random.randint(1, 5)
        content = random.choice(["很好", "不错", "一般", "有待提高", "强烈推荐"])
        is_visible = True
        created_at = (datetime.utcnow() - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d %H:%M:%S.%f")
        updated_at = created_at
        reviews.append((user_id, book_id, rating, content, is_visible, created_at, updated_at))
    return reviews

def generate_favorites(user_ids, book_ids, n=40):
    """生成收藏"""
    favorites = []
    # 确保不重复
    pairs = set()
    for _ in range(n):
        user_id = random.choice(user_ids)
        book_id = random.choice(book_ids)
        if (user_id, book_id) in pairs:
            continue
        pairs.add((user_id, book_id))
        created_at = (datetime.utcnow() - timedelta(days=random.randint(1, 60))).strftime("%Y-%m-%d %H:%M:%S.%f")
        favorites.append((user_id, book_id, created_at))
    return favorites

def insert_data():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()

    # 插入用户
    users = generate_users(20)
    cursor.executemany('''
        INSERT INTO users (username, email, hashed_password, full_name, role, is_active, max_borrow_count, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', users)

    # 插入图书
    books = generate_books(20)
    cursor.executemany('''
        INSERT INTO books (name, preview_image, book_number, shelf_location, quantity, available_quantity,
                          author, isbn, publisher, publish_date, price, description, category_id, tags,
                          borrow_count, avg_rating, review_count, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', books)

    # 获取新插入的用户ID和图书ID
    cursor.execute("SELECT id FROM users WHERE username LIKE 'user%'")
    user_ids = [row[0] for row in cursor.fetchall()]
    cursor.execute("SELECT id FROM books WHERE name LIKE '图书%'")
    book_ids = [row[0] for row in cursor.fetchall()]

    # 生成借阅记录
    borrow_records = generate_borrow_records(user_ids, book_ids, n_per_user=2)
    if borrow_records:
        cursor.executemany('''
            INSERT INTO borrow_records (user_id, book_id, borrow_date, due_date, return_date, status, renew_count, fine_amount, fine_paid, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', borrow_records)

    # 生成评论
    reviews = generate_reviews(user_ids, book_ids, n=30)
    if reviews:
        cursor.executemany('''
            INSERT INTO book_reviews (user_id, book_id, rating, content, is_visible, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', reviews)

    # 生成收藏
    favorites = generate_favorites(user_ids, book_ids, n=40)
    if favorites:
        cursor.executemany('''
            INSERT INTO favorites (user_id, book_id, created_at)
            VALUES (?, ?, ?)
        ''', favorites)

    conn.commit()
    conn.close()
    print(f"插入了 {len(users)} 个用户, {len(books)} 本书籍, {len(borrow_records)} 条借阅记录, {len(reviews)} 条评论, {len(favorites)} 个收藏。")

if __name__ == "__main__":
    insert_data()