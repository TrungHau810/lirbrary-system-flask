from flask import Flask, render_template, request, abort

from . import app
from .dao import search_books, get_book, get_all_authors, get_all_publishers, get_popular_books, get_books_by_category
from .models import Category


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

    print(data)


    
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

if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=5000)