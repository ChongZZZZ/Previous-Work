from flask import Flask, request, jsonify, render_template
from datetime import datetime, timedelta
import json
import logging
import pytz

app = Flask(__name__)

from SmartScheduler import SmartScheduler, ClassSchedule, Task, ReinforcementLearningAgent

# Initialize the SmartScheduler and ReinforcementLearningAgent
scheduler = SmartScheduler()
rl_agent = ReinforcementLearningAgent(n_actions=3) 
logging.basicConfig(level=logging.DEBUG)

# Add timezone constant
CHICAGO_TZ = pytz.timezone('America/Chicago')

def get_chicago_now():
    return datetime.now(CHICAGO_TZ)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/add_class')
def add_class_page():
    return render_template('add_class.html')

@app.route('/set_work_block')
def set_work_block_page():
    return render_template('set_work_block.html')

@app.route('/add_task')
def add_task_page():
    return render_template('add_task.html')

@app.route('/daily_schedule')
def daily_schedule_page():
    return render_template('daily_schedule.html')

@app.route('/set_work_block', methods=['POST'])
def set_work_block():
    data = request.json
    for day, times in data.items():
        start_time = datetime.strptime(times['start'], '%H:%M').time()
        end_time = datetime.strptime(times['end'], '%H:%M').time()
        scheduler.set_working_hours(day, start_time, end_time)
    return jsonify({"message": "Work block set successfully"})

@app.route('/add_class', methods=['POST'])
def add_class():
    data = request.json
    name = data['name']
    days = data['days']
    start_time = datetime.strptime(data['start_time'], '%H:%M').time()
    end_time = datetime.strptime(data['end_time'], '%H:%M').time()
    class_schedule = ClassSchedule(name, days, start_time, end_time)
    scheduler.add_class(class_schedule)
    return jsonify({"message": "Class added successfully"})

@app.route('/add_task', methods=['POST'])
def add_task():
    data = request.json
    name = data['name']
    deadline = datetime.strptime(data['deadline'], '%Y-%m-%d')
    tag = data['tag']
    estimated_time = int(data['estimated_time'])
    task = Task(name, deadline, tag, estimated_time)
    scheduler.add_task(task)
    return jsonify({"message": "Task added successfully"})

@app.route('/update_daily_schedule', methods=['GET'])
def update_daily_schedule():
    date_str = request.args.get('date')
    date = datetime.strptime(date_str, '%Y-%m-%d').date()
    user_preferences = {
        'tag': request.args.get('tag', 'homework'),
        'priority': float(request.args.get('priority', 1)),
        'estimated_time': int(request.args.get('estimated_time', 180))
        }
    schedule = scheduler.update_daily_schedule(date, user_preferences)
    return jsonify(schedule)


@app.route('/get_next_task', methods=['POST'])
def get_next_task():
    data = request.json
    user_preferences = data['user_preferences']
    current_energy = data['current_energy']
    
    next_task = scheduler.get_next_task(user_preferences, current_energy)
    
    if next_task:
        return jsonify({
            "name": next_task.name,
            "deadline": next_task.deadline.strftime('%Y-%m-%d'),
            "tag": next_task.tag,
            "estimated_time": next_task.estimated_time,
            "energy_level": scheduler.get_task_energy_level(next_task)
        })



@app.route('/mark_task_finished', methods=['POST'])
def mark_task_finished():
    data = request.json
    task_name = data['task_name']
    actual_time = int(data['actual_time'])
    current_energy = data['current_energy']
        
    task = next((task for task in scheduler.tasks if task.name == task_name), None)
    if task:
        scheduler.mark_task_finished(task_name, actual_time)
            
        chicago_now = get_chicago_now()
        return jsonify({
            "task_info": {
                "name": task_name,
                "actual_time": actual_time,
                "completion_time": chicago_now.strftime('%H:%M')
                }
            })

@app.route('/get_daily_summary')
def get_daily_summary():
    date_str = request.args.get('date')
    date = datetime.strptime(date_str, '%Y-%m-%d').date()
    summary = scheduler.get_daily_summary(date)
    return jsonify(summary)
        
@app.route('/get_weekly_summary')
def get_weekly_summary():
    chicago_now = get_chicago_now()
    today = chicago_now.date()
    monday = today - timedelta(days=today.weekday())
        
    summary = scheduler.get_weekly_summary(monday)
    return jsonify(summary)

    
if __name__ == '__main__':
    app.run(debug=True)