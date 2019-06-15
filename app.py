import os
from flask import Flask, flash, redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash


# Configure application
app = Flask(__name__)

# Configure sql base
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sql_db.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    password = db.Column(db.String(256))
    email = db.Column(db.String(120))
    photo = db.Column(db.String(256))

    def __repr__(self):
        return '<User %r>' % self.username


@app.route("/")
def index():
    # Render the final template
    print(__name__)
    return render_template("index.html")


@app.route("/company")
def corp_page():
    """Get user info"""

    return render_template("company.html")


@app.route("/client", methods=["GET", "POST"])
def client():
    """Add photo to bd"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Add User
        user = User(username=request.form.get("username"))
        db.session.add(user)
        db.session.commit()

        # Save photo
        file = request.files['file']
        file.save(os.path.join('img/', str(user.id)))

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("client.html")

