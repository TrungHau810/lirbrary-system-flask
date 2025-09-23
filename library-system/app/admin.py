import datetime

from flask import render_template, request, flash, redirect, url_for, abort
from flask_login import login_required

from app import app, dao
from app.auth.decorators import role_required
from app.dao import update_user, count_books
from app.models import User


@app.route("/admin")
@login_required
@role_required(["ADMIN"])
def admin_index():
    return render_template("index.html")


# User management
@app.route("/admin/users")
@login_required
@role_required(["ADMIN"])
def admin_users():
    user_list = dao.get_users()
    return render_template("admin/users.html",
                           users=user_list)


@app.route("/admin/users/add", methods=["GET", "POST"])
@login_required
@role_required(["ADMIN"])
def admin_add_user():
    if request.method == "POST":
        username = request.form.get("username")
        fullname = request.form.get("full_name")
        avatar = request.files["avatar"] if "avatar" in request.files else None
        confirm_password = request.form.get("confirm_password")
        email = request.form.get("email")
        password = request.form.get("password")
        role = request.form.get("user_role")

        if password != confirm_password:
            flash("Mật khẩu xác nhận không khớp", "danger")
            return redirect(url_for("admin_add_user"))

        if dao.get_user_by_username(username):
            flash("Tên đăng nhập đã tồn tại", "danger")
            return redirect(url_for("admin_add_user"))
        if dao.get_user_by_email(email):
            flash("Email đã tồn tại", "danger")
            return redirect(url_for("admin_add_user"))

        try:
            dao.add_user(username, fullname, avatar, email, password, role)
            flash("Thêm người dùng thành công!", "success")
            return redirect(url_for("admin_users"))
        except Exception as ex:
            flash("Có lỗi xảy ra khi thêm người dùng: %s" % ex, "danger")

    return render_template("admin/user_form.html")


@app.route("/admin/users/delete/<int:user_id>", methods=["GET", "POST"])
@login_required
@role_required(["ADMIN"])
def admin_delete_user(user_id):
    if dao.delete_user(user_id):
        flash("Xóa người dùng thành công!", "success")
    else:
        flash("Có lỗi xảy ra khi xóa người dùng", "danger")
    return redirect(url_for("admin_users"))


@app.route("/admin/users/edit/<int:user_id>", methods=["GET", "POST"])
@login_required
@role_required(["ADMIN"])
def admin_edit_user(user_id):
    u = User.query.get(user_id)
    if not u:
        abort(404)

    if request.method == "POST":
        username = request.form.get("username")
        fullname = request.form.get("full_name")
        avatar = request.files["avatar"] if "avatar" in request.files else None
        confirm_password = request.form.get("confirm_password")
        email = request.form.get("email")
        password = request.form.get("password")
        role = request.form.get("user_role")

        if password != confirm_password:
            flash("Mật khẩu xác nhận không khớp", "danger")
            return redirect(url_for("admin_add_user"))

        user = update_user(user_id, username, fullname, avatar, email, password, role)
        if user:
            flash("Cập nhật người dùng thành công!", "success")
            return redirect(url_for("admin_users"))
        else:
            flash("Có lỗi xảy ra khi cập nhật người dùng", "danger")

    return render_template("admin/user_form.html", user=u)


# Book management
@app.route("/admin/books")
@login_required
@role_required(["ADMIN"])
def admin_books():
    books = dao.get_books()
    return render_template("admin/admin_books.html", books=books)


@app.route("/admin/books/add", methods=["GET", "POST"])
@login_required
@role_required(["ADMIN"])
def admin_add_book():
    authors = dao.get_all_authors()
    categories = dao.get_all_categories()
    publishers = dao.get_all_publishers()
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        image = request.files["image"] if "image" in request.files else None
        author_id = request.form.get("author_id", type=int)
        category_id = request.form.get("category_id", type=int)
        publisher_id = request.form.get("publisher_id", type=int)
        isbn = request.form.get("isbn")
        price = request.form.get("price", type=int)
        quantity = request.form.get("quantity", type=int)
        print("Data: ", name, description, image, author_id, category_id, publisher_id, isbn, price, quantity)
        try:
            dao.add_or_update_book(None, name, description, image, author_id, category_id, publisher_id, quantity, price)
            flash("Thêm sách thành công!", "success")
            return redirect(url_for("admin_books"))
        except Exception as ex:
            flash("Có lỗi xảy ra khi thêm sách: %s" % ex, "danger")
    return render_template("admin/admin_book_form.html",
                           book={},
                           authors=authors,
                           categories=categories,
                           publishers=publishers)


@app.route("/admin/books/edit/<int:book_id>", methods=["GET", "POST"])
@login_required
@role_required(["ADMIN"])
def admin_edit_book(book_id):
    book = dao.get_book(book_id)
    authors = dao.get_all_authors()
    categories = dao.get_all_categories()
    publishers = dao.get_all_publishers()
    if not book:
        abort(404)

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        image = request.files["image"] if "image" in request.files else None
        author_id = request.form.get("author_id", type=int)
        category_id = request.form.get("category_id", type=int)
        publisher_id = request.form.get("publisher_id", type=int)
        isbn = request.form.get("isbn")
        price = request.form.get("price", type=int)
        quantity = request.form.get("quantity", type=int)

        print("Data: ", name, description, image, author_id, category_id, publisher_id, isbn, price, quantity)
        updated_book = dao.add_or_update_book(book_id, name, description, image, author_id, category_id, publisher_id, quantity, price)
        if updated_book:
            flash("Cập nhật sách thành công!", "success")
            return redirect(url_for("admin_books"))
        else:
            flash("Có lỗi xảy ra khi cập nhật sách", "danger")
    return render_template("admin/admin_book_form.html", book=book,
                           authors=authors, categories=categories, publishers=publishers)


# Thống kê
@app.route("/admin/stats")
@login_required
@role_required(["ADMIN"])
def admin_stats():
    count_book = dao.count_books()
    count_user = dao.count_users()
    borrowed = dao.count_borrowed_slip()
    count_borrow_slip_by_month = dao.count_borrowed_slip_by_month()
    count_unreturn = dao.count_unreturned_slip()
    borrowed_rate = dao.borrowing_return_rate()
    return render_template("admin/stats.html",
                           count_books=count_book,
                           count_users=count_user,
                           borrowed=borrowed,
                           count_unreturn=count_unreturn,
                           borrowed_rate=borrowed_rate,
                           count_borrow_slip_by_month=count_borrow_slip_by_month,
                           )


@app.route('/admin/borrow-request', methods=['GET'])
@login_required
@role_required(['ADMIN'])
def admin_borrow_request():
    borrow_requests = dao.get_list_requests()
    print(borrow_requests)
    return render_template('admin/borrow_requests.html', borrow_requests=borrow_requests)


@app.route("/admin/rule", methods=["GET", "POST"])
@login_required
@role_required(["ADMIN"])
def admin_rule():
    rules = dao.get_rules()
    return render_template("admin/rule.html", rules=rules)


@app.route("/admin/rule/edit/<int:rule_id>", methods=["GET", "POST"])
@login_required
@role_required(["ADMIN"])
def admin_edit_rule(rule_id):
    rule = dao.get_rule_by_id(rule_id)
    if not rule:
        abort(404)

    if request.method == "POST":
        name = request.form.get("name")
        value = request.form.get("value", type=int)

        updated_rule = dao.update_rule(rule_id, name, value)
        if updated_rule:
            flash("Cập nhật quy định thành công!", "success")
            return redirect(url_for("admin_rule"))
        else:
            flash("Có lỗi xảy ra khi cập nhật quy định", "danger")

    return render_template("admin/rule_detail.html", rule=rule)


@app.route("/admin/rule/add", methods=["GET", "POST"])
@login_required
@role_required(["ADMIN"])
def admin_add_rule():
    if request.method == "POST":
        name = request.form.get("name")
        value = request.form.get("value", type=int)

        try:
            dao.add_rule(name, value)
            flash("Thêm quy định thành công!", "success")
            return redirect(url_for("admin_rule"))
        except Exception as ex:
            flash("Có lỗi xảy ra khi thêm quy định: %s" % ex, "danger")

    return render_template("admin/rule_detail.html", rule={})


@app.route("/admin/rule/delete/<int:rule_id>", methods=["GET", "POST"])
@login_required
@role_required(["ADMIN"])
def admin_delete_rule(rule_id):
    if dao.delete_rule(rule_id):
        flash("Xóa quy định thành công!", "success")
    else:
        flash("Có lỗi xảy ra khi xóa quy định", "danger")
    return redirect(url_for("admin_rule"))
