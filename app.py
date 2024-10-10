from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, validators
from wtfforms.validators import DataRequired

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management (flashing messages)


# Configure MySQL connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/library_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the Book model
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    year_published = db.Column(db.Integer, nullable=True)

class BookForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    year_published = IntegerField('Year Published')
    submit = SubmitField('Submit')


# Create the database tables
with app.app_context():
    db.create_all()

@app.route('/add-book/<title>/<author>/<float:price>/<int:year_published>', methods=['GET'])
def add_book(title, author, price, year_published):
    new_book = Book(title=title, author=author, price=price, year_published=year_published)
    db.session.add(new_book)
    db.session.commit()
    return jsonify({'message': 'Book added successfully!'})

@app.route("/add-book", methods=["GET", "POST"])
def add_book():
    form = BookForm()
    if form.validate_on_submit():
        new_book = Book(
            title=form.title.data,
            author=form.author.data,
            price=form.price.data,
            year_published=form.year_published.data
        )
        db.session.add(new_book)
        db.session.commit()
        flash('Book added successfully!')
        return redirect(url_for('get_books'))
    return render_template("add_book.html", form=form)

@app.route('/update-book/<int:id>/<title>/<author>/<float:price>/<int:year_published>', methods=['PUT'])
def update_book(id, title, author, price, year_published):
    book = Book.query.get_or_404(id)
    book.title = title
    book.author = author
    book.price = price
    book.year_published = year_published
    db.session.commit()
    return jsonify({'message': 'Book updated successfully!'})

@app.route("/update-book/<int:id>", methods=["GET", "POST"])
def update_book(id):
    book = Book.query.get_or_404(id)
    form = BookForm(obj=book)
    if form.validate_on_submit():
        book.title = form.title.data
        book.author = form.author.data
        book.price = form.price.data
        book.year_published = form.year_published.data
        db.session.commit()
        flash('Book updated successfully!')
        return redirect(url_for('get_books'))
    return render_template("update_book.html", form=form)

@app.route('/delete-book/<int:id>', methods=['DELETE'])
def delete_book(id):
    book = Book.query.get_or_404(id)
    db.session.delete(book)
    db.session.commit()
    return jsonify({'message': 'Book deleted successfully!'})



@app.route('/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    books_list = [{'id': book.id, 'title': book.title, 'author': book.author, 'price': book.price, 'year_published': book.year_published} for book in books]
    return jsonify(books_list)

# Define User model if needed
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

# Flask-WTF form for handling user input
class UserForm(FlaskForm):
    name = StringField('Name', validators=[validators.DataRequired()])
    email = StringField('Email', validators=[validators.DataRequired(), validators.Email()])
    submit = SubmitField('Submit')

@app.route("/")
def index():
    users = User.query.all()
    return render_template("list_users.html", users=users)

@app.route("/add-user", methods=["GET", "POST"])
def add_user():
    form = UserForm()
    if form.validate_on_submit():
        new_user = User(name=form.name.data, email=form.email.data)
        db.session.add(new_user)
        db.session.commit()
        flash('User added successfully!')
        return redirect(url_for('index'))
    return render_template("add_user.html", form=form)

@app.route("/update-user/<int:id>", methods=["GET", "POST"])
def update_user(id):
    user = User.query.get_or_404(id)
    form = UserForm(obj=user)
    if form.validate_on_submit():
        user.name = form.name.data
        user.email = form.email.data
        db.session.commit()
        flash('User updated successfully!')
        return redirect(url_for('index'))
    return render_template("update_user.html", form=form)

if __name__ == "__main__":
    app.run(debug=True)
