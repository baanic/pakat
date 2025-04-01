from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import json
import os
from datetime import datetime, timedelta
import jdatetime
from models import db, Task
from auth import auth

app = Flask(__name__)
app.secret_key = "secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///pakat.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
app.register_blueprint(auth)
DATA_FILE = "data/tasks.json"

def load_tasks():
    if not os.path.exists(DATA_FILE): return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_tasks(tasks):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

def jalali_date(iso_date):
    try:
        g_date = datetime.fromisoformat(iso_date)
        j_date = jdatetime.date.fromgregorian(date=g_date.date())
        return j_date.strftime("%Y/%m/%d")
    except:
        return "نامشخص"

@app.route("/")
def dashboard():
    if "user" not in session:
        return redirect(url_for("auth.login"))

    user_id = session.get("user")
    tasks = Task.query.filter_by(user_id=user_id).all()

    today = datetime.today().date()
    tomorrow = today + timedelta(days=1)
    week = today + timedelta(days=7)

    def categorize(task):
        if task.completed: return "nodate"
        if not task.date: return "nodate"
        try:
            d = datetime.fromisoformat(task.date).date()
            if d <= today: return "today"
            elif d == tomorrow: return "tomorrow"
            elif d <= week: return "week"
        except: return "nodate"
        return "nodate"

    categorized = {"today": [], "tomorrow": [], "week": [], "nodate": []}
    for task in tasks:
        task.jalali_time = jdatetime.date.fromgregorian(date=datetime.fromisoformat(task.date).date()).strftime("%Y/%m/%d") if task.date else ""
        categorized[categorize(task)].append(task)

    return render_template("dashboard.html",
        tasks_today=categorized["today"],
        tasks_tomorrow=categorized["tomorrow"],
        tasks_week=categorized["week"],
        tasks_nodate=categorized["nodate"]
    )

@app.route("/add-task", methods=["POST"])
def add_task():
    data = request.get_json()
    tasks = load_tasks()
    new_task = {
        "id": max([t["id"] for t in tasks], default=0) + 1,
        "title": data.get("title", ""),
        "date": "",
        "priority": "medium",
        "completed": False,
        "tags": []
    }
    tasks.append(new_task)
    save_tasks(tasks)
    return jsonify({"ok": True})

@app.route("/delete-task", methods=["POST"])
def delete_task():
    task_id = request.json.get("id")
    tasks = load_tasks()
    tasks = [t for t in tasks if t["id"] != task_id]
    save_tasks(tasks)
    return jsonify({"status": "deleted"})

@app.route("/complete-task", methods=["POST"])
def complete_task():
    task_id = request.json.get("id")
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            task["completed"] = True
            break
    save_tasks(tasks)
    return jsonify({"status": "completed"})

@app.route("/reorder-tasks", methods=["POST"])
def reorder_tasks():
    ids = request.json.get("order", [])
    tasks = load_tasks()
    task_map = {t["id"]: t for t in tasks}
    new_order = [task_map[i] for i in ids if i in task_map]
    save_tasks(new_order)
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(debug=True)