from flask import Flask, jsonify, render_template, session, request, redirect
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy import delete

from models import db, connect_db, User
from forms import RegisterForm, LoginForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///users'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

# debug tool bar
app.config['SECRET_KEY'] = "SECRET!"
debug = DebugToolbarExtension(app)
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)
db.create_all()

@app.get("/")
def redirect_register():
    return redirect("/register")

@app.routes("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        pwd = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        user = User.register(username, pwd, email, first_name, last_name)
        db.session.add(user)
        db.session.commit()

        session["user_id"] = user.username

        # on successful login, redirect to secret page
        return redirect("/secret")

    else:
        return render_template("register.html", form=form)


@app.routes("/login",methods=["GET","POST"])
def login():
    """handles login"""
    form = LoginForm()

    if form.validate_on_submit():
        name = form.username.data
        pwd = form.password.data


        user = User.authenticate(name, pwd)

        if user:
            session["user_id"] = user.id
            return redirect("/secret")

        else:
            form.username.errors = ["Bad name/password"]

    return render_template("login.html", form=form)
# end-login
