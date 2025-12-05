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

def insert_data():
    conn = sqlite3.connect('backend/library.db')
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

    conn.commit()
    conn.close()
    print(f"插入了 {len(users)} 个用户和 {len(books)} 本书籍。")

if __name__ == "__main__":
    insert_data()