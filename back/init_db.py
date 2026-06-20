from app import app, db
from models import User

def init_database():
    with app.app_context():
        db.create_all()
        print("✓ Таблицы созданы")
        
        if User.query.count() == 0:
            doctor = User(name="Доктор Хаус", role="doctor")
            db.session.add(doctor)
            
            patient = User(name="Иван Иванов", role="patient")
            db.session.add(patient)
            
            db.session.commit()
            print("✓ Тестовые данные добавлены:")
            print(f"  - Врач: {doctor.name} (ID: {doctor.id})")
            print(f"  - Пациент: {patient.name} (ID: {patient.id})")
        else:
            print("✓ База данных уже инициализирована")

if __name__ == '__main__':
    init_database()