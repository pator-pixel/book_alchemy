from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import os

from data_models import db, Author, Book

app = Flask(__name__)
app.secret_key = "library-secret-key"

basedir = os.path.abspath(os.path.dirname(__file__))

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"
)

db.init_app(app)


@app.route("/")
def home():
    sort_by = request.args.get("sort", "title")
    search_query = request.args.get("search", "")

    query = Book.query

    if search_query:
        query = query.filter(Book.title.ilike(f"%{search_query}%"))

    if sort_by == "author":
        books = query.join(Author).order_by(Author.name).all()
    elif sort_by == "year":
        books = query.order_by(Book.publication_year).all()
    else:
        books = query.order_by(Book.title).all()

    return render_template(
        "home.html",
        books=books,
        search_query=search_query
    )


@app.route("/book/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    author = book.author

    db.session.delete(book)
    db.session.commit()

    if author and len(author.books) == 0:
        db.session.delete(author)
        db.session.commit()

    flash("Book deleted successfully!")

    return redirect(url_for("home"))


@app.route("/add_author", methods=["GET", "POST"])
def add_author():
    message = ""

    if request.method == "POST":
        name = request.form.get("name")

        birth_date = datetime.strptime(
            request.form.get("birth_date"),
            "%Y-%m-%d"
        ).date()

        date_of_death_input = request.form.get("date_of_death")
        date_of_death = None

        if date_of_death_input:
            date_of_death = datetime.strptime(
                date_of_death_input,
                "%Y-%m-%d"
            ).date()

        author = Author(
            name=name,
            birth_date=birth_date,
            date_of_death=date_of_death
        )

        db.session.add(author)
        db.session.commit()

        message = "Author added successfully!"

    return render_template("add_author.html", message=message)


@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    message = ""
    authors = Author.query.order_by(Author.name).all()

    if request.method == "POST":
        book = Book(
            isbn=request.form.get("isbn"),
            title=request.form.get("title"),
            publication_year=int(request.form.get("publication_year")),
            author_id=int(request.form.get("author_id"))
        )

        db.session.add(book)
        db.session.commit()

        message = "Book added successfully!"

    return render_template(
        "add_book.html",
        authors=authors,
        message=message
    )


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)