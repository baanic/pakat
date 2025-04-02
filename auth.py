from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

auth = Blueprint("auth", __name__)

@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        existing = User.query.filter_by(username=username).first()
        if existing:
            return "نام کاربری قبلاً ثبت شده است."
        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("auth.login"))
    return '''
    <!DOCTYPE html>
    <html lang="fa">
    <head><meta charset="UTF-8"><title>ثبت‌نام</title></head>
    <body>
        <h2>فرم ثبت‌نام</h2>
        <form method="POST">
            <label>نام کاربری:</label>
            <input type="text" name="username" required><br>
            <label>رمز عبور:</label>
            <input type="password" name="password" required><br>
            <button type="submit">ثبت‌نام</button>
        </form>
    </body>
    </html>
    '''

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            return "اطلاعات ورود نادرست است."
        session["user"] = user.id
        return redirect(url_for("dashboard"))
    return '''
    <!DOCTYPE html>
    <html lang="fa">
    <head><meta charset="UTF-8"><title>ورود</title></head>
    <body>
        <h2>فرم ورود</h2>
        <form method="POST">
            <label>نام کاربری:</label>
            <input type="text" name="username" required><br>
            <label>رمز عبور:</label>
            <input type="password" name="password" required><br>
            <button type="submit">ورود</button>
        </form>
    </body>
    </html>
    '''

@auth.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("auth.login"))