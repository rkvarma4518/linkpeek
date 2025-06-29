# from flask import Blueprint, render_template, request
# from flask_login import login_required, current_user

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
import os
from werkzeug.utils import secure_filename

from app import db
from app.models import ProviderProfile

provider = Blueprint('provider', __name__, url_prefix='/provider')

@provider.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'provider':
        return "Unauthorized", 403
    return render_template('provider/dashboard.html')

@provider.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if current_user.role != 'provider':
        return "Unauthorized", 403

    profile = current_user.profile or ProviderProfile(user_id=current_user.id)

    if request.method == 'POST':
        profile.full_name = request.form.get('full_name')
        profile.email = request.form.get('email')
        profile.phone = request.form.get('phone')
        profile.address = request.form.get('address')
        profile.service_info = request.form.get('service_info')

        image_file = request.files.get('image')
        video_file = request.files.get('video')

        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)

        if image_file and image_file.filename:
            image_filename = secure_filename(image_file.filename)
            image_path = os.path.join(upload_folder, image_filename)
            image_file.save(image_path)
            profile.image_path = image_filename

        if video_file and video_file.filename:
            video_filename = secure_filename(video_file.filename)
            video_path = os.path.join(upload_folder, video_filename)
            video_file.save(video_path)
            profile.video_path = video_filename

        db.session.add(profile)
        db.session.commit()
        flash("Profile updated successfully!")
        return redirect(url_for('provider.dashboard'))

    return render_template('provider/edit_profile.html', profile=profile)
