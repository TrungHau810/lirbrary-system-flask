import hashlib
import json
from sqlalchemy import or_
from .models import Book, Category, Author, Publisher, User


def auth_user(username, password):
    with open("../app/data/users.json", encoding='utf-8') as f:
        users = json.load(f)

        for u in users:
            if u['username'] == username and u['password'] == password:
                return True

    return False


def login_user(username, password):
    user = User.query.filter_by(username=username).first()
    if user and user.password == str(hashlib.md5(password.encode('utf-8')).hexdigest()):
        return user

    return None


def get_users():
    user_list = User.query.all()
    return user_list


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


if __name__ == "__main__":
    print(auth_user("user", 345))
