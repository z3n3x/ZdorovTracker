from flask import Flask, jsonify, request
from flask_cors import CORS
from models import db, User, Task, TaskCompletion, WellbeingLog
from datetime import datetime

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///medication_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/api/users', methods=['GET'])
def get_users():
    """Получить список всех пользователей (для экрана выбора роли)"""
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@app.route('/api/patients/<int:patient_id>/schedule', methods=['GET'])
def get_patient_schedule(patient_id):
    date = request.args.get('date')
    
    if not date:
        return jsonify({'error': 'Параметр date обязателен'}), 400
    
    tasks = Task.query.filter(
        Task.patient_id == patient_id
    ).all()
    
    schedule = []
    for task in tasks:
        if date in task.dates:

            completion = TaskCompletion.query.filter_by(
                task_id=task.id,
                date=date
            ).first()
            
            task_data = task.to_dict()
            task_data['is_completed'] = completion.is_completed if completion else False
            task_data['completed_at'] = completion.completed_at.isoformat() if completion and completion.completed_at else None
            
            schedule.append(task_data)

    wellbeing = WellbeingLog.query.filter_by(
        patient_id=patient_id,
        date=date
    ).first()
    
    return jsonify({
        'date': date,
        'tasks': schedule,
        'wellbeing': wellbeing.to_dict() if wellbeing else None
    })

@app.route('/api/patients/<int:patient_id>/tasks/<int:task_id>/complete', methods=['POST'])
def complete_task(patient_id, task_id):
    date = request.args.get('date')
    
    if not date:
        return jsonify({'error': 'Параметр date обязателен'}), 400
    
    task = Task.query.filter_by(id=task_id, patient_id=patient_id).first()
    if not task:
        return jsonify({'error': 'Задача не найдена'}), 404
    
    completion = TaskCompletion.query.filter_by(
        task_id=task_id,
        date=date
    ).first()
    
    if completion:
        completion.is_completed = True
        completion.completed_at = datetime.utcnow()
    else:
        completion = TaskCompletion(
            task_id=task_id,
            date=date,
            is_completed=True,
            completed_at=datetime.utcnow()
        )
        db.session.add(completion)
    
    db.session.commit()
    
    return jsonify(completion.to_dict())

@app.route('/api/patients/<int:patient_id>/wellbeing', methods=['POST'])
def save_wellbeing(patient_id):
    data = request.get_json()
    date = data.get('date')
    text = data.get('text')
    
    if not date or not text:
        return jsonify({'error': 'Поля date и text обязательны'}), 400
    
    log = WellbeingLog.query.filter_by(
        patient_id=patient_id,
        date=date
    ).first()
    
    if log:
        log.text = text
    else:
        # Создаем новую
        log = WellbeingLog(
            patient_id=patient_id,
            date=date,
            text=text
        )
        db.session.add(log)
    
    db.session.commit()
    
    return jsonify(log.to_dict())

@app.route('/api/doctors/<int:doctor_id>/patients', methods=['GET'])
def get_doctor_patients(doctor_id):
    patients = User.query.filter_by(role='patient').all()
    return jsonify([patient.to_dict() for patient in patients])

@app.route('/api/doctors/<int:doctor_id>/patients/<int:patient_id>/dashboard', methods=['GET'])
def get_patient_dashboard(doctor_id, patient_id):
    tasks = Task.query.filter_by(patient_id=patient_id).all()
    
    tasks_data = []
    for task in tasks:
        task_dict = task.to_dict()
        completions = TaskCompletion.query.filter_by(task_id=task.id).all()
        task_dict['completions'] = {c.date: c.to_dict() for c in completions}
        tasks_data.append(task_dict)
    
    wellbeing_logs = WellbeingLog.query.filter_by(patient_id=patient_id).all()
    
    return jsonify({
        'tasks': tasks_data,
        'wellbeing_logs': [log.to_dict() for log in wellbeing_logs]
    })

@app.route('/api/doctors/<int:doctor_id>/tasks', methods=['POST'])
def create_task(doctor_id):
    data = request.get_json()
    
    patient_id = data.get('patient_id')
    text = data.get('text')
    dates = data.get('dates')  # Массив дат
    
    if not patient_id or not text or not dates:
        return jsonify({'error': 'Поля patient_id, text и dates обязательны'}), 400
    
    task = Task(
        doctor_id=doctor_id,
        patient_id=patient_id,
        text=text,
        dates=dates
    )
    
    db.session.add(task)
    db.session.commit()
    
    return jsonify(task.to_dict()), 201

@app.route('/api/patients/<int:patient_id>/calendar', methods=['GET'])
def get_patient_calendar(patient_id):
    month = request.args.get('month')
    
    if not month:
        return jsonify({'error': 'Параметр month обязателен (формат YYYY-MM)'}), 400
    

    tasks = Task.query.filter_by(patient_id=patient_id).all()

    calendar_data = {}
    
    for task in tasks:
        for date_str in task.dates:
            if date_str.startswith(month):
                if date_str not in calendar_data:
                    calendar_data[date_str] = {
                        'total_tasks': 0,
                        'completed_tasks': 0,
                        'task_ids': []
                    }
                
                calendar_data[date_str]['total_tasks'] += 1
                calendar_data[date_str]['task_ids'].append(task.id)
                
                completion = TaskCompletion.query.filter_by(
                    task_id=task.id,
                    date=date_str
                ).first()
                
                if completion and completion.is_completed:
                    calendar_data[date_str]['completed_tasks'] += 1
    
    return jsonify({
        'month': month,
        'days': calendar_data
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)