from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from auth import auth_bp
from models import db, Task
from flask_migrate import Migrate
import jdatetime

app = Flask(__name__)
app.secret_key = "replace-this-with-env-var"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init database
db.init_app(app)
with app.app_context():
    db.create_all()

migrate = Migrate(app, db)

# Register authentication blueprint
app.register_blueprint(auth_bp)

@app.route('/')
def index():
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    week_later = today + timedelta(days=7)

    tasks_today = Task.query.filter(Task.due_date == today, Task.completed == False).all()
    tasks_tomorrow = Task.query.filter(Task.due_date == tomorrow, Task.completed == False).all()
    tasks_week = Task.query.filter(Task.due_date > tomorrow, Task.due_date <= week_later, Task.completed == False).all()
    tasks_no_date = Task.query.filter((Task.due_date == None) & (Task.completed == False)).all()
    tasks_completed = Task.query.filter(Task.completed == True).all()

    return render_template('index.html',
        tasks_today=tasks_today,
        tasks_tomorrow=tasks_tomorrow,
        tasks_week=tasks_week,
        tasks_no_date=tasks_no_date,
        tasks_completed=tasks_completed,
        jdatetime=jdatetime
    )

@app.route('/add-task', methods=['POST'])
def add_task():
    title = request.form.get('title')
    due_date = request.form.get('due_date')

    if not title:
        flash("عنوان نمی‌تونه خالی باشه.", 'error')
        return redirect(url_for('index'))

    if due_date:
        try:
            due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
        except ValueError:
            flash("تاریخ نامعتبر است.", 'error')
            return redirect(url_for('index'))
    else:
        due_date = None

    task = Task(title=title, due_date=due_date)
    db.session.add(task)
    db.session.commit()
    flash("وظیفه با موفقیت اضافه شد!", 'success')
    return redirect(url_for('index'))

@app.route('/delete-task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    flash("وظیفه حذف شد.", 'success')
    return redirect(url_for('index'))

@app.route('/complete-task/<int:task_id>', methods=['POST'])
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.completed = True
    db.session.commit()
    flash("وظیفه با موفقیت کامل شد!", 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
