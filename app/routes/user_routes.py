from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_login import login_required, current_user
from app.models import User
from app.models import ProviderProfile
from app.models import Rating
from app import db

user = Blueprint('user', __name__, url_prefix='/user')

@user.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'user':
        return "Unauthorized", 403
    providers = User.query.filter_by(role='provider', verified=True).all()
    return render_template('user/dashboard.html', providers=providers)


@user.route('/providers')
@login_required
def view_providers():
    profession = request.args.get('profession', '').strip().lower()
    address = request.args.get('address', '').strip().lower()

    query = User.query.filter(User.role == 'provider', User.verified == True)

    if profession:
        query = query.filter(User.profession.ilike(f"%{profession}%"))

    if address:
        query = query.join(User.profile).filter(ProviderProfile.address.ilike(f"%{address}%"))

    providers = query.all()

    return render_template(
        'user/view_providers.html',
        providers=providers,
        profession=profession,
        address=address
    )


@user.route('/rate/<int:provider_id>', methods=['POST'])
@login_required
def rate_provider(provider_id):
    provider = User.query.filter_by(id=provider_id, role='provider').first_or_404()
    stars = int(request.form['rating'])
    comment = request.form.get('comment')

    rating = Rating(user_id=current_user.id, provider_id=provider.id,
                    rating=stars, comment=comment)
    db.session.add(rating)
    db.session.commit()
    flash("Thank you for your feedback!")
    return redirect(url_for('user.view_providers'))