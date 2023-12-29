from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz  # Change time zone
import logging
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todo.sqlite"
app.config["SECRET_KEY"] = "SECRET_KEY"  # Add a secret key for session management
logging.basicConfig(filename='app.log', level=logging.INFO)
# how to get a secret key
# In your command line >>> access Python >>> then type:

# OS Approach
# import os
# os.urandom(14)

# UUID Approach
# import uuid
# uuid.uuid4().hex

# Secrets [ only for Python 3.6 + ]
#import secrets
# secrets.token_urlsafe(14)

db = SQLAlchemy(app)

# Creating Table Todo
class Todo(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"{self.sno} - {self.title}"

# Simple login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        input_password = request.form.get('password')
        
        # Check if the hardcoded password matches the input
        if input_password == '1234':
            session['logged_in'] = True
            return redirect('/')
        else:
            return render_template('login.html', error="Invalid password")

    return render_template('login.html')

# Home route for displaying and adding new items
@app.route('/', methods=["GET", "POST"])
def home():
    # Check if the user is logged in
    if not session.get('logged_in'):
        return redirect('/login')

    if request.method == "POST":
        user_title = request.form["title"]
        user_desc = request.form["desc"]

        ist_tz = pytz.timezone('Asia/Kolkata')
        ist_datetime = datetime.now(tz=ist_tz)
        date_format = '%d-%m-%Y %H:%M:%S'
        date_str = ist_datetime.strftime(date_format)
        date_created = datetime.strptime(date_str, date_format)

        todo = Todo(title=user_title, desc=user_desc, date_created=date_created)
        db.session.add(todo)
        db.session.commit()

    all_items = Todo.query.all()
    return render_template("index.html", all_todos=all_items)

# Update route
@app.route("/update/<int:sno>", methods=["GET", "POST"])
def update_item(sno):
    # Check if the user is logged in
    if not session.get('logged_in'):
        return redirect('/login')

    if request.method == "POST":
        user_title = request.form["title"]
        user_desc = request.form["desc"]

        item = Todo.query.get_or_404(sno)
        item.title = user_title
        item.desc = user_desc
        db.session.add(item)
        db.session.commit()
        return redirect("/")

    item = Todo.query.get_or_404(sno)
    return render_template("update.html", todo=item)

# Delete route
@app.route('/delete/<int:sno>')
def delete_item(sno):
    # Check if the user is logged in
    if not session.get('logged_in'):
        return redirect('/login')

    item = Todo.query.get_or_404(sno)
    db.session.delete(item)
    db.session.commit()
    return redirect('/')

# Search route
@app.route('/search', methods=["GET", "POST"])
def search_item():
    # Check if the user is logged in
    if not session.get('logged_in'):
        return redirect('/login')

    # Get the search query from the URL parameter
    search_query = request.args.get('query')

    # Perform the search query
    result = Todo.query.filter(Todo.title == search_query).all()

    # Render the result
    return render_template('result.html', posts=result)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8023, debug=True)
