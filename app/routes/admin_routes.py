from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import User
from app import db

admin = Blueprint('admin', __name__, url_prefix='/admin')

@admin.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'admin':
        return "Unauthorized", 403
    users = User.query.filter(User.role != 'admin').all()
    return render_template('admin/dashboard.html', users=users)

@admin.route('/verify/<int:user_id>')
@login_required
def verify(user_id):
    if current_user.role != 'admin':
        return "Unauthorized", 403
    user = User.query.get_or_404(user_id)
    if user.role != 'provider':
        flash('Only providers can be verified')
        return redirect(url_for('admin.dashboard'))
    user.verified = True
    db.session.commit()
    flash(f'Provider {user.username} verified!')
    return redirect(url_for('admin.dashboard'))

@admin.route('/delete/<int:user_id>')
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        return "Unauthorized", 403
    user = User.query.get_or_404(user_id)
    if user.role == 'admin':
        flash('Cannot delete admin')
        return redirect(url_for('admin.dashboard'))
    db.session.delete(user)
    db.session.commit()
    flash(f'User {user.username} deleted.')
    return redirect(url_for('admin.dashboard'))
