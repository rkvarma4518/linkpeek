from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app import db
import random
from flask_mail import Message
from app import mail

auth = Blueprint('auth', __name__, url_prefix='/auth')

@auth.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        entered_otp = request.form['otp']
        if entered_otp == session.get('otp'):
            user_data = session.get('pending_user')
            if not user_data:
                flash("Session expired. Please register again.")
                return redirect(url_for('auth.register'))

            # Create the user
            new_user = User(
                username=user_data['username'],
                email=user_data['email'],
                role=user_data['role'],
                password=user_data['password'],  # already hashed
                is_email_verified=True
            )
            db.session.add(new_user)
            db.session.commit()

            session.pop('otp', None)
            session.pop('pending_user', None)

            flash('Email verified! You can now log in.')
            return redirect(url_for('auth.login'))
        else:
            flash('Incorrect OTP. Please try again.')

    return render_template('auth/verify_otp.html')

# @auth.route('/register', methods=['GET', 'POST'])
# def register():
#     if current_user.is_authenticated:
#         return redirect(url_for(f'{current_user.role}.dashboard'))
#     if request.method == 'POST':
#         username = request.form['username']
#         email = request.form['email']
#         password = request.form['password']
#         role = request.form['role']
#         contact = request.form['contact']
#         profession = request.form.get('profession')  # optional for providers
#         about = request.form.get('about')

#         if User.query.filter_by(username=username).first():
#             flash('Username already exists')
#             return redirect(url_for('auth.register'))
#         if User.query.filter_by(email=email).first():
#             flash('Email already registered')
#             return redirect(url_for('auth.register'))

#         hashed_password = generate_password_hash(password, method='sha256')

#         new_user = User(username=username, email=email, password=hashed_password,
#                         role=role, contact=contact, profession=profession, about=about)
#         db.session.add(new_user)
#         db.session.commit()
#         flash('Registration successful! Please login. Providers need verification.')
#         return redirect(url_for('auth.login'))

#     return render_template('auth/register.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for(f'{current_user.role}.dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        contact = request.form['contact']
        profession = request.form.get('profession')
        about = request.form.get('about')

        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('auth.register'))
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('auth.register'))

        # ✅ Hash password
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # ✅ Generate OTP
        otp = str(random.randint(100000, 999999))

        # ✅ Store pending registration in session
        session['pending_user'] = {
            'username': username,
            'email': email,
            'password': hashed_password,
            'role': role,
            'contact': contact,
            'profession': profession,
            'about': about
        }
        session['otp'] = otp

        # ✅ Send email
        msg = Message("Your OTP Code", sender="your_email@gmail.com", recipients=[email])
        msg.body = f"Your verification OTP is: {otp}"
        mail.send(msg)

        flash("OTP sent to your email. Please verify to complete registration.")
        return redirect(url_for('auth.verify_otp'))

    return render_template('auth/register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for(f'{current_user.role}.dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))

        login_user(user)
        flash(f'Welcome back, {user.username}!')
        return redirect(url_for(f'{user.role}.dashboard'))

    return render_template('auth/login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.')
    return redirect(url_for('auth.login'))
