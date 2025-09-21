from flask import render_template, request, redirect, url_for, flash
from . import app
from .dao import search_books
from .models import Category



@app.route('/admin/manage_books')
def manage_books():
    kw = request.args.get('kw')
    category_id = request.args.get('category_id', type=int)
    books = search_books(keyword=kw, category_id=category_id)
    categories = Category.query.order_by(Category.name.asc()).all()

    return render_template("admin/books.html",
                           books=books,
                           categories=categories,
                           kw=kw,
                           category_id=category_id)


@app.route("/admin/manage_books/add")
def add_book_view():
    return render_template("admin/book_form.html")


@app.route('/admin/manage_books/edit/<int:book_id>')
def edit_book_view(book_id):
    return render_template('admin/book_form.html')


@app.route('/admin/manage_books/delete/<int:book_id>')
def delete_book_view(book_id):
    return redirect(url_for('manage_books'))
