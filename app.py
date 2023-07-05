from flask import Flask, render_template, request, redirect

app = Flask(__name__)
tasks = []

@app.route('/')
def index():
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['POST'])
def add_task():
    task = request.form['task']
    tasks.append(task)
    return redirect('/')

@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    if (request.method == 'POST'):
        new_task = request.form['task']
        tasks[task_id] = new_task
        return redirect('/')
    
    task = tasks[task_id]
    return render_template('edit.html', task=task, task_id=task_id)

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    del tasks[task_id]
    return redirect('/')
