from re import template
from flask import Flask, flash, jsonify, render_template, session, request, redirect
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy import delete

from models import Note, db, connect_db, User, Note
from forms import NotesForm, RegisterForm, LoginForm, UpdateNotesForm, CSRFProtectForm

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

USER_SESSION_KEY = "username"

@app.get("/")
def redirect_register():
    """redirects user to /register page"""
    return redirect("/register")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Shows register form handles form submission will redirect back to /register
    if form is not validated, if validated redirects to /user/<username>."""
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

        session["user"] = user.username

        # on successful login, redirect to secret page
        return redirect("/user/<username>")

    else:
        return render_template("register.html", form=form)


@app.route("/login",methods=["GET","POST"])
def login():
    """handles login if login successful redirects to /user/<username> else
    redirects to login.html"""
    form = LoginForm()

    if form.validate_on_submit():
        name = form.username.data
        pwd = form.password.data


        user = User.authenticate(name, pwd)

        if user:
            session[USER_SESSION_KEY] = user.username
            return redirect(f"/user/{user.username}")

        else:
            form.username.errors = ["Bad name/password"]

    return render_template("login.html", form=form)

@app.get("/user/<username>")
def display_secret(username):
    """If user not logged in and tries to access unauthorized page, redirects to
    login handles logged in users trying to go to UNAUTHORIZED pages.
     to ("/").  """


    if USER_SESSION_KEY not in session:
        flash("You must be logged in")
        return redirect("/login")

    elif session[USER_SESSION_KEY] != username:
        flash("Wrong user!")
        return redirect("/")

    form = CSRFProtectForm()
    user = User.query.get_or_404(username)
    return render_template("user_detail_page.html", user=user,form=form)

@app.post("/logout")
def logout():
    """handles logout pops user out of session"""
    form = CSRFProtectForm()

    if form.validate_on_submit():
        session.pop(USER_SESSION_KEY, None)

    return redirect("/")

@app.post("/users/<username>/delete")
def delete_user(username):
    """Delete a user from the database and delete all notes
        Clear user info in the session and redirect("/")"""

    user = User.query.get_or_404(username)
    form = CSRFProtectForm()

    if form.validate_on_submit():
        notes = user.notes

        for note in notes:
            db.session.delete(note)

        db.session.delete(user)
        db.session.commit()

        session.pop(USER_SESSION_KEY, None)
        return redirect("/")

    else:
        return redirect("/users/<username>")

@app.route("/users/<username>/notes/add", methods= ["GET","POST"])
def add_note(username):
    """ Add a note and redirect to user's detail page
        or display the form to add a note"""

    user = User.query.get_or_404(username)
    form = NotesForm()


    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        owner = user.username
        note = Note(title=title,content=content,owner=owner)
        db.session.add(note)
        db.session.commit()

        return redirect(f"/user/{username}")

    else:
        return render_template("notes_form.html", form=form)

@app.route("/notes/<note_id>/update", methods=["GET", "POST"])
def update_note(note_id):
    """ Update a note and redirect to the user's detail page """

    note = Note.query.get_or_404(note_id)
    form = UpdateNotesForm()

    if form.validate_on_submit():
        note.title = form.data.get("title", note.title)
        note.content = form.data.get("content", note.content)

        db.session.commit()

        return redirect(f"/user/{note.user.username}")

    else:
        return render_template("update_note_form.html", form=form)

@app.post("/notes/<note_id>/delete")
def delete_note(note_id):
    """ Delete a note and redirect to the user's detail page """

    note = Note.query.get_or_404(note_id)
    form = CSRFProtectForm()
    username = note.user.username

    if form.validate_on_submit():
        note = Note.query.get_or_404(note_id)
        username = username
        db.session.delete(note)
        db.session.commit()

    return redirect(f"/user/{username}")
