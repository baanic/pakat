
from flask import Blueprint, render_template, request, redirect, url_for, session
import json
import os
import hashlib

auth = Blueprint('auth', __name__)
USER_FILE = "data/users.json"

def load_users():
    if not os.path.exists(USER_FILE): return {}
    with open(USER_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def hash_pass(password):
    return hashlib.sha256(password.encode()).hexdigest()

@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        users = load_users()
        username = request.form.get("username")
        password = request.form.get("password")
        if username in users:
            return "کاربر قبلاً وجود دارد"
        users[username] = hash_pass(password)
        save_users(users)
        return redirect(url_for("auth.login"))
    return render_template("register.html")

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        users = load_users()
        username = request.form.get("username")
        password = request.form.get("password")
        if username in users and users[username] == hash_pass(password):
            session["user"] = username
            return redirect(url_for("dashboard"))
        return "اطلاعات ورود اشتباه است"
    return render_template("login.html")

@auth.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("auth.login"))
