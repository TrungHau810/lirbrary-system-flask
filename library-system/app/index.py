import hashlib

from flask import Flask, render_template, request, abort, flash, redirect, url_for
from werkzeug.security import generate_password_hash
from . import app, db
from .dao import search_books, get_book, get_all_authors, get_all_publishers, get_popular_books, get_books_by_category, \
    get_users, login_user
from .models import Category, User, UserRole


@app.route("/")
def index():
    popular_books = get_popular_books(8)
    categories = Category.query.order_by(Category.name.asc()).all()
    return render_template("index.html", popular_books=popular_books, categories=categories)

@app.route("/books")
def books():
    kw = request.args.get("kw")
    cat = request.args.get("category_id", type=int)
    author = request.args.get("author_id", type=int)
    publisher = request.args.get("publisher_id", type=int)


    data = search_books(kw, cat, author, publisher)


    categories = Category.query.order_by(Category.name.asc()).all()
    authors = get_all_authors()
    publishers = get_all_publishers()

    return render_template("books.html",
                         books=data,
                         categories=categories,
                         authors=authors,
                         publishers=publishers,
                         kw=kw,
                         category_id=cat,
                         author_id=author,
                         publisher_id=publisher)

@app.route("/books/<int:book_id>")
def book_detail(book_id):
    b = get_book(book_id)
    if not b:
        abort(404)

    related_books = []
    if b.category_id:
        related_books = get_books_by_category(b.category_id, 4)
        related_books = [book for book in related_books if book.id != b.id]

    return render_template("book_detail.html", b=b, related_books=related_books)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = login_user(username, password)
        if user:
            flash("Đăng nhập thành công!", "success")
            return redirect(url_for("index"))
        else:
            flash("Sai tên đăng nhập hoặc mật khẩu", "danger")
            return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        fullname = request.form.get("fullname")
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        email = request.form.get("email")

        if password != confirm_password:
            flash("Mật khẩu xác nhận không khớp", "danger")
            return redirect(url_for("register"))

        if User.query.filter_by(username=username).first():
            flash("Tên đăng nhập đã tồn tại", "danger")
            return redirect(url_for("register"))
        if User.query.filter_by(email=email).first():
            flash("Email đã tồn tại", "danger")
            return redirect(url_for("register"))

        new_user = User(
            username=username,
            full_name=fullname,
            email=email,
            password=str(hashlib.md5(password.encode('utf-8')).hexdigest()),
            avatar="default.png",
            user_role=UserRole.STUDENT
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Đăng ký thành công!", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/admin")
def admin_index():
    return render_template("index.html")

@app.route("/admin/users")
def admin_users():
    user_list = get_users()
    return render_template("admin/users.html",
                           users=user_list)


@app.route("/admin/users/add")
def admin_add_user():
    return render_template("admin/user_form.html")


@app.route("/admin/users/edit/<int:user_id>")
def admin_edit_user(user_id):
    u = User.query.get(user_id)
    if not u:
        abort(404)

    return render_template("admin/user_form.html", user=u)

if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=5000)