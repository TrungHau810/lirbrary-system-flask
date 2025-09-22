import hashlib
import json
from collections import OrderedDict
from datetime import datetime

import cloudinary.uploader
from sqlalchemy import or_, extract, func

from app import db
from .models import Book, Category, Author, Publisher, User, BorrowingSlip, BorrowingSlipDetail, Rule


def auth_user(username, password):
    with open("../app/data/users.json", encoding='utf-8') as f:
        users = json.load(f)

        for u in users:
            if u['username'] == username and u['password'] == password:
                return True

    return False


def login_account(username, password):
    user = User.query.filter_by(username=username).first()
    if user and user.password == str(hashlib.md5(password.encode('utf-8')).hexdigest()):
        return user

    return None


def add_user(username, fullname, avatar, email, password, role):
    new_user = User(
        username=username,
        full_name=fullname,
        email=email,
        password=str(hashlib.md5(password.encode('utf-8')).hexdigest()),
        user_role=role
    )

    if avatar:
        res = cloudinary.uploader.upload(avatar)
        print(res)
        new_user.avatar = res.get('secure_url')

    db.session.add(new_user)
    db.session.commit()


def update_user(user_id, username, fullname, avatar, email, password, role):
    u = User.query.get(user_id)
    if not u:
        return False

    u.username = username
    u.full_name = fullname
    u.email = email
    u.user_role = role

    if password:
        u.password = str(hashlib.md5(password.encode('utf-8')).hexdigest())

    if avatar:
        res = cloudinary.uploader.upload(avatar)
        u.avatar = res.get('secure_url')

    db.session.commit()
    return True


def delete_user(user_id):
    u = User.query.get(user_id)
    if not u:
        return False

    db.session.delete(u)
    db.session.commit()
    return True


def get_users():
    user_list = User.query.all()
    return user_list


def get_user_by_username(username: str) -> User | None:
    return User.query.filter_by(username=username).first()


def get_user_by_email(email: str) -> User | None:
    return User.query.filter_by(email=email).first()


def get_books():
    return Book.query.order_by(Book.created_date.desc()).all()


def count_books():
    return Book.query.count()


def count_users():
    return User.query.count()


# Số lượt mượn sách
def count_borrowed_slip():
    return BorrowingSlip.query.count()


def count_borrowed_slip_by_month():
    year = datetime.now().year  # Năm hiện tại

    # Truy vấn số lượt mượn theo tháng
    results = db.session.query(
        extract('month', BorrowingSlip.created_date).label('month'),
        func.count(BorrowingSlip.id).label('borrowed_count')
    ).filter(
        extract('year', BorrowingSlip.created_date) == year
    ).group_by(
        extract('month', BorrowingSlip.created_date)
    ).order_by('month').all()

    # Khởi tạo dict 12 tháng, mặc định 0
    borrowed_by_month = OrderedDict((str(m), 0) for m in range(1, 13))

    # Điền số liệu thực tế
    for month, count in results:
        borrowed_by_month[str(int(month))] = count

    return borrowed_by_month


# Số phiếu mượn chưa trả
def count_unreturned_slip():
    return BorrowingSlip.query.filter(
        or_(
            BorrowingSlip.is_return == False,
            BorrowingSlip.is_return.is_(None)
        )
    ).count()


# Tỉ lệ mượn trả sách
def borrowing_return_rate():
    total_slips = BorrowingSlip.query.count()
    if not total_slips:
        return 0.0

    # Đếm phiếu đã trả (is_return = True)
    returned_slips = BorrowingSlip.query.filter(BorrowingSlip.is_return ==True).count()

    # Tính tỉ lệ và làm tròn 2 chữ số
    return round((returned_slips / total_slips) * 100, 2)


def get_rules():
    return Rule.query.all()

def get_rule_by_id(rule_id: int) -> Rule | None:
    return Rule.query.get(rule_id)

def update_rule(rule_id: int, name: str, value: int):
    rule = Rule.query.get(rule_id)
    if not rule:
        return None

    rule.name = name
    rule.value = value
    db.session.commit()
    return rule

def add_rule(name: str, value: int):
    new_rule = Rule(name=name, value=value)
    db.session.add(new_rule)
    db.session.commit()
    return new_rule

def delete_rule(rule_id: int):
    rule = Rule.query.get(rule_id)
    if not rule:
        return False

    db.session.delete(rule)
    db.session.commit()
    return True

def search_books(keyword: str | None = None, category_id: int | None = None, author_id: int | None = None,
                 publisher_id: int | None = None):
    q = Book.query.join(Author, Book.author_id == Author.id, isouter=True) \
        .join(Publisher, Book.publisher_id == Publisher.id, isouter=True) \
        .join(Category, Book.category_id == Category.id, isouter=True)

    if keyword:
        kw = f"%{keyword.strip()}%"
        q = q.filter(or_(
            Book.name.ilike(kw),
            Author.name.ilike(kw),
            Publisher.name.ilike(kw),
            Book.isbn.ilike(kw),
            Book.description.ilike(kw)
        ))

    if category_id:
        q = q.filter(Book.category_id == category_id)

    if author_id:
        print(author_id)
        q = q.filter(Book.author_id == author_id)
        print(q)

    if publisher_id:
        q = q.filter(Book.publisher_id == publisher_id)

    return q.order_by(Book.created_date.desc()).all()


def get_book(book_id: int) -> Book | None:
    return Book.query.get(book_id)


def get_all_authors():
    return Author.query.order_by(Author.name.asc()).all()


def get_all_publishers():
    return Publisher.query.order_by(Publisher.name.asc()).all()


def get_popular_books(limit=10):
    return Book.query.filter(Book.available_quantity > 0).order_by(Book.created_date.desc()).limit(limit).all()


def get_books_by_category(category_id: int, limit=10):
    return Book.query.filter(Book.category_id == category_id, Book.available_quantity > 0).limit(limit).all()


def get_list_requests():
    requests = BorrowingSlip.query.all()
    for r in requests:
        r.total = BorrowingSlipDetail.query.filter(BorrowingSlipDetail.id_borrowing_slip == r.id).count()

    return requests


if __name__ == "__main__":
    print(auth_user("user", 345))
