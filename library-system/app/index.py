import hashlib
from datetime import timedelta

from click import confirm
from flask import Flask, render_template, request, abort, flash, redirect, url_for, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from . import app, db
from .dao import search_books, get_book, get_all_authors, get_all_publishers, get_popular_books, get_books_by_category, \
    get_users, login_account, get_list_requests, add_user, update_user, get_user_by_username, get_user_by_email, \
    delete_user, create_borrowing_slip, get_borrowing_slip_by_user, get_rule_date_return
from .auth.decorators import role_required
from .models import Category, User, UserRole, Book, Author, Publisher, BorrowingSlip, StatusEnum, Fine


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

        user = login_account(username, password)
        if user:
            login_user(user)
            flash("Đăng nhập thành công!", "success")
            return redirect(url_for("index"))
        else:
            flash("Sai tên đăng nhập hoặc mật khẩu", "danger")
            return redirect(url_for("login"))
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash('Bạn đã đăng xuất', 'info')
    return redirect(url_for("index"))


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


# func nay phan theo role
@app.route("/staff/books/new", methods=["GET", "POST"])
@login_required
@role_required(["ADMIN", "STAFF"])
def create_book():
    categories = Category.query.order_by(Category.name.asc()).all()
    authors = get_all_authors()
    publishers = get_all_publishers()

    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        image = (request.form.get("image") or "").strip() or None
        description = (request.form.get("description") or "").strip()
        isbn = (request.form.get("isbn") or "").strip() or None
        language = (request.form.get("language") or "Tiếng Việt").strip()

        def to_int(val, default=None):
            try:
                return int(val)
            except (TypeError, ValueError):
                return default

        price = to_int(request.form.get("price"), 0)
        quantity = to_int(request.form.get("quantity"), 1)
        available_quantity = to_int(request.form.get("available_quantity"), quantity)
        publication_year = to_int(request.form.get("publication_year"))
        pages = to_int(request.form.get("pages"))

        # Resolve foreign keys (existing or create new)
        category_id = request.form.get("category_id")
        author_id = request.form.get("author_id")
        publisher_id = request.form.get("publisher_id")

        new_category = (request.form.get("new_category") or "").strip()
        new_author = (request.form.get("new_author") or "").strip()
        new_publisher = (request.form.get("new_publisher") or "").strip()

        if not name or not description:
            flash("Vui lòng nhập tên sách và mô tả", "warning")
            return render_template("staff_book_form.html",
                                   categories=categories, authors=authors, publishers=publishers)

        try:
            if new_category:
                c = Category(name=new_category)
                db.session.add(c)
                db.session.flush()
                category_id = c.id
            else:
                category_id = int(category_id) if category_id else None

            if new_author:
                a = Author(name=new_author)
                db.session.add(a)
                db.session.flush()
                author_id = a.id
            else:
                author_id = int(author_id) if author_id else None

            if new_publisher:
                p = Publisher(name=new_publisher)
                db.session.add(p)
                db.session.flush()
                publisher_id = p.id
            else:
                publisher_id = int(publisher_id) if publisher_id else None

            book = Book(
                name=name,
                image=image,
                price=price or 0,
                quantity=quantity or 1,
                available_quantity=available_quantity if available_quantity is not None else (quantity or 1),
                description=description,
                isbn=isbn,
                publication_year=publication_year,
                pages=pages,
                language=language or 'Tiếng Việt',
                category_id=category_id,
                author_id=author_id,
                publisher_id=publisher_id,
            )
            db.session.add(book)
            db.session.commit()
            flash("Đã thêm sách mới thành công!", "success")
            return redirect(url_for("book_detail", book_id=book.id))
        except Exception as ex:
            db.session.rollback()
            flash("Có lỗi xảy ra khi lưu sách: %s" % ex, "danger")

    return render_template("staff_book_form.html", categories=categories, authors=authors, publishers=publishers)


# Lấy danh sách các yêu cầu mượn sách
@app.route("/staff/borrow-requests")
@login_required
@role_required(["ADMIN", "STAFF"])
def borrow_requests():
    data = get_list_requests()
    for r in data:
        print(r.user.full_name)
        print(r.status)
    return render_template("borrow_requests.html",
                           list_requests=data)


# Xem chi tiết yêu cầu mượn sách
@app.route("/staff/borrow-requests/<int:slip_id>")
@login_required
@role_required(["ADMIN", "STAFF"])
def borrow_request_detail(slip_id):
    slip = BorrowingSlip.query.get_or_404(slip_id)
    fine_count = Fine.query.filter_by(id_user=slip.id_user).count()
    return render_template("borrow_request_detail.html", slip=slip, fine_count=fine_count)


# Duyệt yêu cầu mượn sách
@app.route("/staff/borrow-requests/<int:slip_id>/update", methods=["POST"])
@login_required
@role_required(["ADMIN", "STAFF"])
def update_borrow_requests(slip_id):
    slip = BorrowingSlip.query.get(slip_id)
    data = request.get_json()
    status = data.get("status")

    if status not in ["APPROVED", "REJECTED"]:
        return jsonify({"success": False, "message": "Trạng thái không hợp lệ"})
    slip.status = StatusEnum[status]
    if status == "APPROVED":
        for detail in slip.details:
            book = Book.query.get(detail.id_book)
            if book and book.available_quantity > 0:
                book.available_quantity -= 1
            else:
                return jsonify({
                    "success": False,
                    "message": f"Sách {book.name} đã hết số lượng!"
                })
    db.session.commit()
    return jsonify({"success": True, "message": f"Trạng thái đã đổi thành {status}"})


# Danh sách đãng ký mượn sách
@app.route("/my-borrows")
@login_required
@role_required(["STUDENT"])
def my_borrows():
    slips = get_borrowing_slip_by_user(user_id=current_user.id)
    date_return = get_rule_date_return()
    for slip in slips:
        slip.due_date = slip.created_date + timedelta(days=date_return)
    return render_template("my_borrows.html", slips=slips)


@app.route("/borrow")
@login_required
@role_required(["STUDENT"])
def borrow_book():
    book_id = request.args.get("book_id", type=int)
    if not book_id:
        flash("Yêu cầu không hợp lệ!", "danger")
        return None

    book = get_book(book_id)
    if not book or book.available_quantity <= 0:
        flash("Sách không tồn tại hoặc đã hết!", "danger")
        return redirect(url_for("index"))

    existing_request = BorrowingSlip.query.filter_by(id_user=current_user.id, status=StatusEnum.PENDING).first()
    if existing_request:
        flash("Bạn đã có một yêu cầu mượn đang chờ xử lý. Vui lòng đợi hoặc hủy yêu cầu trước.", "warning")
        return redirect(url_for("index"))

    slip = create_borrowing_slip(user_id=current_user.id, book_id=book_id)
    if not slip:
        flash("Có lỗi xảy ra khi tạo yêu cầu mượn sách.", "danger")
        return redirect(url_for("index"))

    flash("Yêu cầu mượn sách đã được gửi thành công!", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=5000)
