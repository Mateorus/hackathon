import os
import cv2
import face_capture
import face_recognition
import json
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
    vector = db.Column(db.String(2700))
    birthday = db.Column(db.String(30))
    cardnumber = db.Column(db.String(30))

    def __repr__(self):
        return '<User %r>' % self.username

@app.after_request
def add_header(response):
   response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
   response.headers['Cache-Control'] = 'public, max-age=0'
   return response

@app.route("/")
def index():
    # Render the final template
    return render_template("index.html")


@app.route("/company")
def corp_page():
    """Get user info"""
    frame = face_capture.face_capture()
    user = User.query.all()
    for el in user:
        print(el)
        known_encoding = face_recognition.face_encodings(frame)[0]
        result = face_recognition.compare_faces([json.loads(el.vector)], known_encoding)
        print(result[0])
        if result[0]:
            return render_template("company.html", username=el.username, email=el.email,
            birthday=el.birthday, cardnumber=el.cardnumber, img=os.path.join('/static/img/', str(el.id)))
    return render_template("fail.html", img='/static/img/fail.png')


@app.route("/client", methods=["GET", "POST"])
def client():
    """Add photo to bd"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Add User
        user = User(username = request.form.get("username"), email = request.form.get("email"),
            birthday = request.form.get("birthday"), cardnumber = request.form.get("cardnumber"))
        db.session.add(user)
        db.session.commit()

        # Save photo
        file = request.files['file']
        file.save(os.path.join('static/img/', str(user.id)))
        img = face_recognition.load_image_file(os.path.join('static/img/', str(user.id)))
        vector = face_recognition.face_encodings(img)[0]
        convert = vector.tolist()
        json_string = json.dumps(convert)
        user.vector = json_string

        db.session.add(user)
        db.session.commit()

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("client.html")

