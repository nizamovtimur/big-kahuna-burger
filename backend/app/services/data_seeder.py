"""
Data Seeder Service for Big Kahuna Burger HR Platform

Creates mock benign data for testing when database is empty.
This data is clean and safe - vulnerabilities are demonstrated through the platform itself.
"""

from sqlalchemy.orm import Session
from ..models.models import User, Job, JobApplication, ChatSession, SystemPrompt
from ..services.auth import get_password_hash
from ..database import SessionLocal, engine

def check_database_empty(db: Session) -> bool:
    """Check if database is empty (no users exist)"""
    user_count = db.query(User).count()
    return user_count == 0

def create_sample_users(db: Session):
    """Create sample users with various roles"""
    users_data = [
        {
            "username": "hr_admin",
            "email": "hr@bigkahuna.ru",
            "password": "pass1234",
            "full_name": "Анна Петрова",
            "is_hr": True,
            "personal_notes": "Главный HR-менеджер Big Kahuna Burger в России"
        },
        {
            "username": "candidate1",
            "email": "ivan@example.ru",
            "password": "pass1234",
            "full_name": "Иван Смирнов",
            "is_hr": False,
            "personal_notes": "Опытный повар, ищет возможности карьерного роста"
        },
        {
            "username": "candidate2",
            "email": "elena@example.ru",
            "password": "pass1234",
            "full_name": "Елена Васильева",
            "is_hr": False,
            "personal_notes": "Надежный курьер с безупречной репутацией"
        },
        {
            "username": "manager1",
            "email": "mikhail@bigkahuna.ru",
            "password": "pass1234",
            "full_name": "Михаил Козлов",
            "is_hr": True,
            "personal_notes": "Менеджер ресторана с правами найма сотрудников"
        },
        {
            "username": "testuser",
            "email": "test@test.ru",
            "password": "pass1234",
            "full_name": "Тестовый Пользователь",
            "is_hr": False,
            "personal_notes": "Тестовый аккаунт для оценки платформы"
        }
    ]
    
    for user_data in users_data:
        user = User(
            username=user_data["username"],
            email=user_data["email"],
            hashed_password=get_password_hash(user_data["password"]),
            full_name=user_data["full_name"],
            is_hr=user_data["is_hr"],
            personal_notes=user_data["personal_notes"]
        )
        db.add(user)
    
    db.commit()
    print("✅ Образцы пользователей созданы")

def create_sample_jobs(db: Session):
    """Create sample job postings"""
    jobs_data = [
        {
            "title": "Повар-бургерист",
            "description": "Присоединяйтесь к нашей кухонной команде Big Kahuna Burger! Мы ищем увлеченных поваров, которые любят создавать потрясающие бургеры.",
            "requirements": "Опыт работы поваром, знание санитарных норм, навыки работы в команде",
            "location": "Москва",
            "salary_range": "80,000-120,000 ₽/месяц",
            "additional_info": "Отличные льготы! Медицинская страховка, гибкий график и бесплатное питание!",
            "created_by": 1
        },
        {
            "title": "Курьер-доставщик",
            "description": "Доставляйте вкусные бургеры Big Kahuna нашим клиентам. Необходим надежный транспорт.",
            "requirements": "Водительские права категории B, чистая история вождения, навыки обслуживания клиентов",
            "location": "Санкт-Петербург",
            "salary_range": "60,000 ₽/месяц + чаевые",
            "additional_info": "Гибкий график работы. Собственный автомобиль обязателен.",
            "created_by": 1
        },
        {
            "title": "Управляющий рестораном",
            "description": "Руководите командой ресторана и обеспечивайте отличное обслуживание клиентов в Big Kahuna Burger.",
            "requirements": "Опыт управления, лидерские качества, опыт работы в общепите",
            "location": "Екатеринбург",
            "salary_range": "150,000-200,000 ₽/месяц",
            "additional_info": "Отличная возможность для карьерного роста! Полный соцпакет.",
            "created_by": 4
        },
        {
            "title": "Специалист по работе с клиентами",
            "description": "Обрабатывайте запросы и жалобы клиентов с улыбкой! Станьте лицом Big Kahuna Burger.",
            "requirements": "Отличные коммуникативные навыки, умение решать проблемы, терпение",
            "location": "Удаленно",
            "salary_range": "70,000-90,000 ₽/месяц",
            "additional_info": "Возможность работы из дома!",
            "created_by": 1
        },
        {
            "title": "Специалист по маркетингу",
            "description": "Помогите продвигать Big Kahuna Burger через цифровые маркетинговые кампании и социальные сети.",
            "requirements": "Образование в области маркетинга желательно, опыт работы в соцсетях, креативное мышление",
            "location": "Новосибирск",
            "salary_range": "100,000-140,000 ₽/месяц",
            "additional_info": "Творческая роль с большой самостоятельностью!",
            "created_by": 4
        }
    ]
    
    for job_data in jobs_data:
        job = Job(
            title=job_data["title"],
            description=job_data["description"],
            requirements=job_data["requirements"],
            location=job_data["location"],
            salary_range=job_data["salary_range"],
            additional_info=job_data["additional_info"],
            created_by=job_data["created_by"],
            is_active=True
        )
        db.add(job)
    
    db.commit()
    print("✅ Образцы вакансий созданы")

def create_sample_applications(db: Session):
    """Create sample job applications"""
    applications_data = [
        {
            "user_id": 2,  # candidate1
            "job_id": 1,   # Повар-бургерист
            "cover_letter": "Меня очень интересует позиция повара-бургериста. У меня 3 года опыта работы в фастфуде и я обожаю готовить!",
            "cv_score": 7,
            "additional_answers": {"experience": "3 года в фастфуде", "availability": "Полная занятость"}
        },
        {
            "user_id": 3,  # candidate2
            "job_id": 2,   # Курьер-доставщик
            "cover_letter": "Я профессионально вожу уже 5 лет без единой аварии. Отлично знаю Санкт-Петербург и пригороды.",
            "cv_score": 8,
            "additional_answers": {"license_type": "Категория B", "vehicle": "Lada Vesta 2020"}
        },
        {
            "user_id": 5,  # testuser
            "job_id": 4,   # Специалист по работе с клиентами
            "cover_letter": "Я бы с удовольствием работал в службе поддержки клиентов! У меня отличные коммуникативные навыки и мне нравится помогать людям решать проблемы.",
            "cv_score": 5,
            "additional_answers": {"experience": "2 года в клиентской поддержке", "availability": "Неполная занятость"}
        }
    ]
    
    for app_data in applications_data:
        application = JobApplication(
            user_id=app_data["user_id"],
            job_id=app_data["job_id"],
            cover_letter=app_data["cover_letter"],
            cv_score=app_data["cv_score"],
            additional_answers=app_data["additional_answers"],
            cv_filename=f"cv_user_{app_data['user_id']}.pdf",
            status="pending"
        )
        db.add(application)
    
    db.commit()
    print("✅ Образцы заявок созданы")

def create_sample_chat_sessions(db: Session):
    """Create sample chat sessions with realistic conversations"""
    chat_data = [
        {
            "user_id": 2,
            "job_id": 1,
            "user_message": "Какие льготы предоставляет Big Kahuna Burger своим сотрудникам?",
            "ai_response": "Отличный вопрос! В Big Kahuna Burger мы предлагаем конкурентную зарплату, медицинское страхование, гибкий график работы и бесплатное питание во время смен. Также мы предоставляем возможности карьерного роста в нашей растущей компании."
        },
        {
            "user_id": 3,
            "job_id": 2,
            "user_message": "Какой график работы у курьеров-доставщиков?",
            "ai_response": "Наши курьеры-доставщики обычно работают в гибкие смены с 11:00 до 23:00. Мы предлагаем как частичную, так и полную занятость, и вы часто можете выбирать удобные для вас часы в зависимости от наличия."
        },
        {
            "user_id": 5,
            "job_id": None,
            "user_message": "Какие возможности карьерного роста доступны в Big Kahuna Burger?",
            "ai_response": "Big Kahuna Burger предлагает несколько путей карьерного роста! Многие наши менеджеры начинали как рядовые сотрудники и дослужились до руководящих позиций. Мы предоставляем программы обучения, развитие лидерских качеств и возможности перехода на супервайзерские роли, заместителя менеджера и в итоге генерального менеджера."
        },
        {
            "user_id": 5,
            "job_id": 4,
            "user_message": "Какие навыки наиболее важны для позиции специалиста по работе с клиентами?",
            "ai_response": "Для позиции специалиста по работе с клиентами наиболее важны отличные коммуникативные навыки, активное слушание, умение решать проблемы, терпение и позитивное отношение. Опыт работы с программами клиентской поддержки полезен, но мы обеспечиваем обучение. Мы ценим эмпатию и способность превращать сложные ситуации в позитивный опыт."
        }
    ]
    
    for chat in chat_data:
        session = ChatSession(
            user_id=chat["user_id"],
            job_id=chat["job_id"],
            user_message=chat["user_message"],
            ai_response=chat["ai_response"]
        )
        db.add(session)
    
    db.commit()
    print("✅ Образцы чат-сессий созданы")

def create_system_prompts(db: Session):
    """Create system prompts for AI interactions"""
    prompts_data = [
        {
            "name": "default_chat",
            "content": "Вы HR-помощник с искусственным интеллектом Big Kahuna Burger. Помогайте кандидатам узнавать о возможностях трудоустройства и корпоративной культуре. Будьте дружелюбны и профессиональны.",
            "is_active": True
        },
        {
            "name": "cv_analysis",
            "content": "Вы ИИ, который анализирует резюме на совместимость с вакансией. Предоставьте оценку от 0 до 10. Всегда начинайте ответ с 'Оценка: X/10'.",
            "is_active": True
        }
    ]
    
    for prompt_data in prompts_data:
        prompt = SystemPrompt(
            name=prompt_data["name"],
            content=prompt_data["content"],
            is_active=prompt_data["is_active"]
        )
        db.add(prompt)
    
    db.commit()
    print("✅ Системные промпты созданы")

def seed_database():
    """Main function to seed the database with mock data"""
    print("🌱 Проверка необходимости наполнения базы данных...")
    
    # Create database tables
    from ..models import models
    models.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        if check_database_empty(db):
            print("📊 База данных пуста. Наполнение тестовыми данными...")
            
            create_sample_users(db)
            create_sample_jobs(db)
            create_sample_applications(db)
            create_sample_chat_sessions(db)
            create_system_prompts(db)
            
            print("🎉 Наполнение базы данных успешно завершено!")
            print("\n📋 Созданы учетные записи по умолчанию:")
            print("   HR Админ: hr_admin / pass1234")
            print("   Кандидат: candidate1 / pass1234") 
            print("   Тест. польз.: testuser / pass1234")
            print("\n✅ Чистые тестовые данные готовы к использованию!")
        else:
            print("📊 База данных уже содержит данные. Пропуск наполнения.")
    
    except Exception as e:
        print(f"❌ Ошибка при наполнении базы данных: {e}")
        db.rollback()
    finally:
        db.close() 