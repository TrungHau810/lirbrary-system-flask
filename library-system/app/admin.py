from flask import render_template, request, redirect, url_for, flash
from . import app, db
from .dao import search_books, get_all_authors, get_all_publishers, add_book, get_book, update_book, \
    delete_book, get_all_categories



# Đây là nơi chúng ta sẽ định nghĩa các trang quản trị
@app.route('/manage_books')
# @login_required # Sẽ bật lên khi có hệ thống đăng nhập hoàn chỉnh
def manage_books():
    # # Kiểm tra quyền admin
    # if current_user.user_role != UserRole.ADMIN:
    #     flash('Bạn không có quyền truy cập trang này!', 'danger')
    #     return redirect(url_for('index'))

    kw = request.args.get('kw')
    category_id = request.args.get('category_id', type=int)

    books = search_books(keyword=kw, category_id=category_id)
    categories = get_all_categories()

    return render_template("admin/books.html",
                           books=books,
                           categories=categories,
                           kw=kw,
                           category_id=category_id)

# Trang thêm sách
@app.route("/books/add", methods=['GET', 'POST'])
def add_book_view():
    if request.method == 'POST':
        book_data = request.form.to_dict()
        try:
            add_book(
                name=book_data.get('name'),
                price=int(book_data.get('price')) if book_data.get('price') else 0,
                quantity=int(book_data.get('quantity')) if book_data.get('quantity') else 0,
                author_id=int(book_data.get('author_id')) if book_data.get('author_id') else None,
                category_id=int(book_data.get('category_id')) if book_data.get('category_id') else None,
                publisher_id=int(book_data.get('publisher_id')) if book_data.get('publisher_id') else None,
                description=book_data.get('description'),
                image=book_data.get('image'),
            )

            flash('Thêm sách mới thành công!', 'success')
            return redirect(url_for('manage_books'))
        except Exception as e:
            flash(f'Thêm sách thất bại! Lỗi: {str(e)}', 'danger')
            return render_template("admin/book_form.html",
                                   legend="Thêm sách mới",
                                   authors=get_all_authors(),
                                   categories=get_all_categories(),
                                   publishers=get_all_publishers(),
                                   book=book_data)

    return render_template("admin/book_form.html",
                           legend="Thêm sách mới",
                           authors=get_all_authors(),
                           categories=get_all_categories(),
                           publishers=get_all_publishers(),
                           book={})  # Truyền vào một dict rỗng

# Sửa sách
@app.route('/books/edit/<int:book_id>', methods=['GET', 'POST'])
# @login_required
def edit_book_view(book_id):
    book = get_book(book_id)
    if not book:
        flash('Sách không tồn tại!', 'danger')
        return redirect(url_for('manage_books'))

    if request.method == 'POST':
        try:
            data = {
                'name': request.form.get('name'),
                'price': request.form.get('price', type=float),
                'quantity': request.form.get('quantity', type=int),
                'author_id': request.form.get('author_id', type=int),
                'category_id': request.form.get('category_id', type=int),
                'publisher_id': request.form.get('publisher_id', type=int),
                'description': request.form.get('description'),
                'image': request.form.get('image')
            }
            update_book(book_id, data)
            flash('Cập nhật sách thành công!', 'success')
            return redirect(url_for('manage_books'))
        except Exception as e:
            flash(f'Cập nhật sách thất bại! Lỗi: {str(e)}', 'danger')

    return render_template('admin/book_form.html',
                           legend=f"Chỉnh sửa sách: {book.name}",
                           book=book,
                           authors=get_all_authors(),
                           categories=get_all_categories(),
                           publishers=get_all_publishers())

# Xóa sách
@app.route('/books/delete/<int:book_id>', methods=['POST'])
# @login_required
def delete_book_view(book_id):
    try:
        delete_book(book_id)
        flash('Xóa sách thành công!', 'success')
    except Exception as e:
        flash(f'Xóa sách thất bại! Lỗi: {str(e)}', 'danger')
    return redirect(url_for('manage_books'))
