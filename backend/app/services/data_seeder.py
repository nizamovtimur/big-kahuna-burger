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
            "email": "hr@bigkahuna.com",
            "password": "secret123",
            "full_name": "HR Administrator",
            "is_hr": True,
            "personal_notes": "Main HR account for Big Kahuna Burger"
        },
        {
            "username": "candidate1",
            "email": "john@example.com",
            "password": "secret123",
            "full_name": "John Candidate",
            "is_hr": False,
            "personal_notes": "Experienced chef looking for opportunities"
        },
        {
            "username": "candidate2",
            "email": "sarah@example.com",
            "password": "password123",
            "full_name": "Sarah Driver",
            "is_hr": False,
            "personal_notes": "Reliable driver with clean record"
        },
        {
            "username": "manager1",
            "email": "mike@bigkahuna.com",
            "password": "admin123",
            "full_name": "Mike Manager",
            "is_hr": True,
            "personal_notes": "Store manager with hiring authority"
        },
        {
            "username": "testuser",
            "email": "test@test.com",
            "password": "test",
            "full_name": "Test User",
            "is_hr": False,
            "personal_notes": "Test account for platform evaluation"
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
    print("✅ Sample users created")

def create_sample_jobs(db: Session):
    """Create sample job postings"""
    jobs_data = [
        {
            "title": "Burger Chef",
            "description": "Join our kitchen team at Big Kahuna Burger! We are looking for passionate cooks who love creating amazing burgers.",
            "requirements": "Experience with cooking, food safety knowledge, teamwork skills",
            "location": "Los Angeles, CA",
            "salary_range": "$15-20/hour",
            "additional_info": "Great benefits! Health insurance, flexible scheduling, and free meals!",
            "created_by": 1
        },
        {
            "title": "Delivery Driver",
            "description": "Deliver delicious Big Kahuna Burgers to our customers. Must have reliable transportation.",
            "requirements": "Valid driver license, clean driving record, customer service skills",
            "location": "Los Angeles, CA",
            "salary_range": "$12/hour + tips",
            "additional_info": "Flexible hours available. Must provide own vehicle.",
            "created_by": 1
        },
        {
            "title": "Restaurant Manager",
            "description": "Lead our restaurant team and ensure excellent customer service at Big Kahuna Burger.",
            "requirements": "Management experience, leadership skills, food service background",
            "location": "Los Angeles, CA",
            "salary_range": "$45,000-55,000/year",
            "additional_info": "Great opportunity for growth! Full benefits package included.",
            "created_by": 4
        },
        {
            "title": "Customer Service Representative",
            "description": "Handle customer inquiries and complaints with a smile! Be the face of Big Kahuna Burger.",
            "requirements": "Excellent communication skills, problem-solving ability, patience",
            "location": "Remote",
            "salary_range": "$14-16/hour",
            "additional_info": "Work from home opportunity!",
            "created_by": 1
        },
        {
            "title": "Marketing Specialist",
            "description": "Help promote Big Kahuna Burger through digital marketing campaigns and social media.",
            "requirements": "Marketing degree preferred, social media experience, creative thinking",
            "location": "San Francisco, CA",
            "salary_range": "$40,000-50,000/year",
            "additional_info": "Creative role with lots of autonomy!",
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
    print("✅ Sample jobs created")

def create_sample_applications(db: Session):
    """Create sample job applications"""
    applications_data = [
        {
            "user_id": 2,  # candidate1
            "job_id": 1,   # Burger Chef
            "cover_letter": "I am very interested in the Burger Chef position. I have 3 years of experience in fast food and love cooking!",
            "cv_score": 7,
            "additional_answers": {"experience": "3 years in fast food", "availability": "Full-time"}
        },
        {
            "user_id": 3,  # candidate2
            "job_id": 2,   # Delivery Driver
            "cover_letter": "I have been driving professionally for 5 years with no accidents. I know the LA area very well.",
            "cv_score": 8,
            "additional_answers": {"license_type": "Class C", "vehicle": "2018 Honda Civic"}
        },
        {
            "user_id": 5,  # testuser
            "job_id": 4,   # Customer Service
            "cover_letter": "I would love to work in customer service! I have great communication skills and enjoy helping people solve problems.",
            "cv_score": 5,
            "additional_answers": {"experience": "2 years customer service", "availability": "Part-time"}
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
    print("✅ Sample applications created")

def create_sample_chat_sessions(db: Session):
    """Create sample chat sessions with realistic conversations"""
    chat_data = [
        {
            "user_id": 2,
            "job_id": 1,
            "user_message": "What are the benefits of working at Big Kahuna Burger?",
            "ai_response": "Great question! At Big Kahuna Burger, we offer competitive wages, health insurance, flexible scheduling, and free meals during your shifts. We also provide opportunities for advancement within our growing company."
        },
        {
            "user_id": 3,
            "job_id": 2,
            "user_message": "What are the working hours for delivery drivers?",
            "ai_response": "Our delivery drivers typically work flexible shifts between 11 AM and 11 PM. We offer both part-time and full-time positions, and you can often choose your preferred hours based on availability."
        },
        {
            "user_id": 5,
            "job_id": None,
            "user_message": "What types of career advancement opportunities are available at Big Kahuna Burger?",
            "ai_response": "Big Kahuna Burger offers several career advancement paths! Many of our managers started as crew members and worked their way up. We provide training programs, leadership development, and opportunities to move into supervisory roles, assistant management, and eventually general management positions."
        },
        {
            "user_id": 5,
            "job_id": 4,
            "user_message": "What skills are most important for the Customer Service Representative position?",
            "ai_response": "For our Customer Service Representative position, the most important skills are excellent communication, active listening, problem-solving abilities, patience, and a positive attitude. Experience with customer service software is helpful but we provide training. We value empathy and the ability to turn challenging situations into positive experiences."
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
    print("✅ Sample chat sessions created")

def create_system_prompts(db: Session):
    """Create system prompts for AI interactions"""
    prompts_data = [
        {
            "name": "default_chat",
            "content": "You are Big Kahuna Burger's AI HR assistant. Help candidates learn about job opportunities and company culture. Be friendly and professional.",
            "is_active": True
        },
        {
            "name": "cv_analysis",
            "content": "You are an AI that analyzes CVs for job compatibility. Provide a score from 0-10. Always start your response with 'Score: X/10'.",
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
    print("✅ System prompts created")

def seed_database():
    """Main function to seed the database with mock data"""
    print("🌱 Checking if database needs seeding...")
    
    # Create database tables
    from ..models import models
    models.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        if check_database_empty(db):
            print("📊 Database is empty. Seeding with mock data...")
            
            create_sample_users(db)
            create_sample_jobs(db)
            create_sample_applications(db)
            create_sample_chat_sessions(db)
            create_system_prompts(db)
            
            print("🎉 Database seeding completed successfully!")
            print("\n📋 Default accounts created:")
            print("   HR Admin: hr_admin / secret123")
            print("   Candidate: candidate1 / secret123")
            print("   Test User: testuser / test")
            print("\n✅ Clean mock data ready for testing!")
        else:
            print("📊 Database already contains data. Skipping seed.")
    
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close() 