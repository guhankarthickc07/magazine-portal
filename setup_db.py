from app import db
from models import User
from werkzeug.security import generate_password_hash

def seed_admin():
    admin = User(
        name="Admin",
        department="Management",
        dob="1990-01-01",
        passed_out_year="",
        location="Head Office",
        email="admin@example.com",
        password=generate_password_hash("admin123"),
        role="Admin",
        profile_img="default.jpg",
        is_approved=True
    )
    
    existing_admin = User.query.filter_by(email="admin@example.com").first()
    if not existing_admin:
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin user created successfully!")
    else:
        print("⚠️ Admin already exists!")

if __name__ == "__main__":
    from app import app
    with app.app_context():
        db.create_all()
        seed_admin()
