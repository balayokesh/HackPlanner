import sqlite3
from flask import Flask, render_template, request, redirect, jsonify
import os
import sendgrid
from sendgrid.helpers.mail import Mail

app = Flask(__name__)

# DB tasks
db = 'tasks.db'
def create_table():
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, task TEXT)')
    conn.commit()
    conn.close()

def fetch_from_db():
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT * FROM tasks')
    tasks = c.fetchall()
    conn.close()
    return tasks

def add_to_db(task):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('INSERT INTO tasks (task) VALUES (?)', (task,))
    conn.commit()
    conn.close()

def edit_at_db(updated_task, id):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('UPDATE tasks SET task = ? WHERE id = ?', (updated_task, id))
    conn.commit()
    conn.close()

def delete_from_db(task_id):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()

# Sendgrid email function
sendgrid_api_key = os.environ('SENDGRID_API_KEY')
from_email = os.environ.get('SENDER_EMAIL')
to_email = os.environ.get('RECEIVER_EMAIL')

def send_email(subject, body):
    message = Mail(
        from_email=from_email,
        to_emails=to_email,
        subject=subject,
        plain_text_content=body)

    try:
        sg = sendgrid.SendGridAPIClient(api_key=sendgrid_api_key)
        response = sg.send(message)
        if response.status_code == 202:
            return True
    except Exception as e:
        print("An error occurred while sending email:", str(e))
    
    return False

# Route definitions
@app.route('/')
def index():
    create_table()
    tasks = fetch_from_db()
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['POST'])
def add_task():
    task = request.form['task']
    add_to_db(task)
    return redirect('/')

@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    if (request.method == 'POST'):
        updated_task = request.form['task']
        edit_at_db(updated_task, task_id)
        return redirect('/')
    
    tasks = fetch_from_db()
    task = next((task[1] for task in tasks if task[0] == task_id), None)
    return render_template('edit.html', task=task, task_id=task_id)

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    delete_from_db(task_id)
    return redirect('/')

@app.route('/send-email', methods=['POST'])
def send_email_route():
    data = request.get_json()
    task = data['task']
    subject = "Reminder: {}".format(task)
    body = "This is a reminder for the task: {}".format(task)

    if send_email(subject, body):
        return jsonify(success=True)
    else:
        return jsonify(success=False), 500
    
if __name__ == '__main__':
    app.run(debug=True)
