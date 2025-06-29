from app import db, create_app
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()
app.app_context().push()

if not User.query.filter_by(username='admin').first():
    admin = User(
        username='admin',
        email='admin@example.com',
        # password=generate_password_hash('admin123', method='pbkdf2:sha256'),
        password = generate_password_hash('admin123'),
        role='admin',
        contact='0000000000'
    )
    db.session.add(admin)
    db.session.commit()
    print("Admin account created.")
else:
    print("Admin user already exists.")
