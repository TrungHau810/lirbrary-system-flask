from enum import Enum as RoleEnum

from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import now


from . import db
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Enum, func


class UserRole(RoleEnum):
    ADMIN = 1
    STAFF = 2
    STUDENT = 3


class User(db.Model, UserMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    avatar = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    user_role = Column(Enum(UserRole), nullable=False, default=UserRole.STUDENT)
    # Relationships
    borrowing_slips = relationship("BorrowingSlip", backref="user", lazy=True)
    receipts = relationship("Receipt", backref="user", lazy=True)


    def __str__(self):
        return self.full_name

    def get_role(self):
        return self.user_role


# Bảng danh mục sách (Thể loại)
class Category(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(String(255), nullable=True)
    books = relationship("Book", backref="category", lazy=True)

    def __str__(self):
        return self.name


# Bảng tác giả
class Author(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    books = relationship("Book", backref="author", lazy=True)

    def __str__(self):
        return self.name


# Bảng nhà xuất bản
class Publisher(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    books = relationship("Book", backref="publisher", lazy=True)

    def __str__(self):
        return f'NXB: {self.name}'



class Book(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    isbn = Column(String(20), nullable=True, unique=True)
    image = Column(String(255), nullable=True)
    price = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    available_quantity = Column(Integer, nullable=False, default=1)
    description = Column(String(1000), nullable=False)
    publication_year = Column(Integer, nullable=True)
    pages = Column(Integer, nullable=True)
    language = Column(String(50), nullable=True, default='Tiếng Việt')
    created_date = Column(DateTime, default=func.now())
    category_id = Column(Integer, ForeignKey(Category.id))
    author_id = Column(Integer, ForeignKey(Author.id))
    publisher_id = Column(Integer, ForeignKey(Publisher.id))
    
    def __str__(self):
        return self.name
    
    @property
    def is_available(self):
        return self.available_quantity > 0



class BorrowingSlip(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_user = Column(Integer, ForeignKey(User.id))
    created_date = Column(DateTime, default=func.now())
    is_return = Column(Boolean, nullable=True, default=False)
    return_date = Column(DateTime, nullable=True)
    # Relationships
    details = relationship("BorrowingSlipDetail", backref="borrowing_slip", lazy=True)



class BorrowingSlipDetail(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_borrowing_slip = Column(Integer, ForeignKey(BorrowingSlip.id))
    id_book = Column(Integer, ForeignKey(Book.id))


# Bảng phiếu nhập sách
class Receipt(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_user = Column(Integer, ForeignKey(User.id), nullable=False)
    date = Column(DateTime, nullable=False, default=func.now())
    details = relationship("ReceiptDetail", backref="receipt", lazy=True)


# Bảng chi tiết phiếu nhập sách
class ReceiptDetail(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_receipt = Column(Integer, ForeignKey(Receipt.id))
    id_book = Column(Integer, ForeignKey(Book.id))
    quantity = Column(Integer, nullable=False, default=1)


# Bảng phiếu phạt tiền
class Fine(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_user = Column(Integer, ForeignKey(User.id), nullable=False)
    amount = Column(Integer, nullable=False)
    reason = Column(String(255), nullable=False)
    date = Column(DateTime, nullable=False, default=func.now())


# Bảng quy định
class Rule(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    value = Column(Integer, nullable=False)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()