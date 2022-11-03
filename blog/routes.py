from flask import Flask, render_template, request, redirect, url_for, flash
from blog import app, db
from .models import User, Post
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_ckeditor import CKEditor

ckeditor = CKEditor()


@app.route("/")
def home():
    posts = Post.query.order_by(Post.date_created.desc()).all()
    return render_template("home.html", posts=posts, user=current_user)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash("Logged in successfully!", category="success")
                login_user(user, remember=True)
                return redirect(url_for("home"))
            else:
                flash("Incorrect password, try again.", category="error")
        else:
            flash("Email does not exist.", category="error")

        
    return render_template("login.html", user=current_user)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        user = User.query.filter_by(email=email).first()

        if user:
            flash("Email address already exists.", category="error")
            return redirect(url_for("signup"))
        elif password != confirm_password:
            flash("Passwords don't match", category="error")
        else:
            
            new_user = User(email=email, firstname=firstname, lastname=lastname, password=generate_password_hash(password, method='sha256'))

            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for("create_post"))
            
    return render_template("register.html", user=current_user)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route("/create-post", methods=["GET", "POST"])
@login_required
def create_post():
    if request.method == "POST":
        text = request.form.get("text")
        if len(text) < 1:
            flash("Post is too short!", category="error")
        else:
            new_post = Post(text=text, author=current_user.id)
            db.session.add(new_post)
            db.session.commit()
            flash("Post created!", category="success")
            return redirect(url_for("home"))

    return render_template("create.html", user=current_user)

@app.route("/post/<firstname>")
def post(firstname):
    user = User.query.filter_by(firstname=firstname).first()
    if not user:
        flash("User not found.", category="error")
        return redirect(url_for("home"))

    posts = user.posts
    return render_template("posts.html", user=current_user, posts=posts, firstname=firstname)

@app.route("/delete/<int:id>")
# @login_required
def delete(id):
    post = Post.query.get_or_404(id)

    try:
        db.session.delete(post)
        db.session.commit()
        return redirect(url_for("home"))
    except:
        flash ("There was a problem deleting that post.", category="error")