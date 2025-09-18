import json
from sqlalchemy import or_
from .models import Book, Category, Author, Publisher
from . import db

def auth_user(username, password):
    with open("../app/data/users.json", encoding='utf-8') as f:
        users = json.load(f)

        for u in users:
            if u['username']==username and u['password']==password:
                return True

    return False

def search_books(keyword: str | None = None, category_id: int | None = None, author_id: int | None = None, publisher_id: int | None = None):
    q = Book.query.join(Author, Book.author_id == Author.id, isouter=True)\
                  .join(Publisher, Book.publisher_id == Publisher.id, isouter=True)\
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


def get_all_categories():
    return Category.query.order_by(Category.name.asc()).all()


def add_author(name: str):
    existing_author = Author.query.filter(Author.name.ilike(name)).first()
    if existing_author:
        return None

    new_author = Author(name=name)
    db.session.add(new_author)
    db.session.commit()
    return new_author


def add_category(name: str):
    existing_category = Category.query.filter(Category.name.ilike(name)).first()
    if existing_category:
        return None

    new_category = Category(name=name)
    db.session.add(new_category)
    db.session.commit()
    return new_category


def add_publisher(name: str):
    existing_publisher = Publisher.query.filter(Publisher.name.ilike(name)).first()
    if existing_publisher:
        return None

    new_publisher = Publisher(name=name)
    db.session.add(new_publisher)
    db.session.commit()
    return new_publisher

def add_book(name, price, quantity, author_id, category_id, publisher_id, description, image=None):
    new_book = Book(
        name=name, price=price, quantity=quantity,
        available_quantity=quantity, author_id=author_id,
        category_id=category_id, publisher_id=publisher_id,
        description=description,
        image=image if image else f'https://placehold.co/300x450/cccccc/ffffff?text={name.replace(" ", "+")}'
    )
    db.session.add(new_book)
    db.session.commit()
    return new_book

def update_book(book_id, data):
    book = get_book(book_id)
    if not book:
        raise ValueError("Sách không tồn tại.")

    for key, value in data.items():
        if value is not None:
            setattr(book, key, value)

    db.session.commit()
    return book

def delete_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        raise Exception("Không tìm thấy sách để xóa!")

    db.session.delete(book)
    db.session.commit()


if __name__=="__main__":
    print(auth_user("user", 345))