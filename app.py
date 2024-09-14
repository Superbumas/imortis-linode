from flask import Flask, render_template, redirect, url_for, flash, request, session, abort, jsonify, send_from_directory, Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, PasswordField, DateField, FileField
from wtforms.validators import DataRequired, Length, ValidationError, EqualTo, Email
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import json

from extensions import db
from forms import DeleteProfileForm, EditProfileForm, EditTimelineForm, RegistrationForm, LoginForm, TimelineForm, SettingsForm, CreateProfileForm, TimelineEventForm
from models import User, Profile
from flask_wtf.csrf import CSRFProtect
from flask_cors import CORS


# Flask app configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = 'ThisIsASecretKey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'png', 'jpeg'}

# Initialize extensions
db.init_app(app)
csrf = CSRFProtect(app)  # Initialize CSRF protection after app is created
CORS(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/home')
def homee():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if the email already exists
        existing_user_email = User.query.filter_by(email=form.email.data).first()
        if existing_user_email:
            flash('Email address already exists. Please use a different email.', 'danger')
            return redirect(url_for('register'))
        
        # Check if the username already exists
        existing_user_username = User.query.filter_by(username=form.username.data).first()
        if existing_user_username:
            flash('Username already exists. Please choose a different username.', 'danger')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        profiles = Profile.query.filter_by(user_id=current_user.id).all()
        delete_form = DeleteProfileForm()
        return render_template('dashboard.html', profiles=profiles, delete_form=delete_form)
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('login'))  # Redirect to login if an error occurs

@app.route('/create_profile', methods=['GET', 'POST'])
@login_required
def create_profile():
    form = CreateProfileForm()
    
    if form.validate_on_submit():
        try:
            profile = Profile(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                bio=form.bio.data,
                date_of_birth=form.date_of_birth.data,
                date_of_death=form.date_of_death.data,
                country=form.country.data,
                city=form.city.data,
                user_id=current_user.id,
                timeline_events=json.loads(form.timeline_events.data) if form.timeline_events.data else []
            )

            if form.profile_picture.data:
                filename = secure_filename(form.profile_picture.data.filename)
                upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                os.makedirs(os.path.dirname(upload_path), exist_ok=True)
                form.profile_picture.data.save(upload_path)
                profile.profile_picture = filename

            if form.cover_photo.data:
                filename = secure_filename(form.cover_photo.data.filename)
                upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                os.makedirs(os.path.dirname(upload_path), exist_ok=True)
                form.cover_photo.data.save(upload_path)
                profile.cover_photo = filename

            db.session.add(profile)
            db.session.commit()
            flash('Profile created successfully!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')

    return render_template('create_profile.html', form=form)

@app.route('/profile/<int:profile_id>', methods=['GET'])
@login_required
def view_profile(profile_id):
    profile = Profile.query.get_or_404(profile_id)
    if profile.user_id != current_user.id:
        abort(403)
    
    # Access timeline events directly from the profile
    timeline_events = profile.timeline_events if profile.timeline_events else []

    print("Profile Picture:", profile.profile_picture)  # Debugging statement
    print("Cover Photo:", profile.cover_photo)  # Debugging statement

    return render_template('view_profile.html', profile=profile, timeline_events=timeline_events)

@app.route('/edit_profile/<int:profile_id>', methods=['GET', 'POST'])
@login_required
def edit_profile(profile_id):
    profile = Profile.query.get_or_404(profile_id)
    if profile.user_id != current_user.id:
        abort(403)
    
    form = EditProfileForm(obj=profile)
    
    if form.validate_on_submit():
        try:
            profile.first_name = form.first_name.data
            profile.last_name = form.last_name.data
            profile.bio = form.bio.data
            profile.date_of_birth = form.date_of_birth.data
            profile.date_of_death = form.date_of_death.data
            profile.country = form.country.data
            profile.city = form.city.data
            profile.timeline_events = json.loads(form.timeline_events.data) if form.timeline_events.data else []

            # Handle profile picture upload
            if form.profile_picture.data and hasattr(form.profile_picture.data, 'filename'):
                filename = secure_filename(form.profile_picture.data.filename)
                upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                os.makedirs(os.path.dirname(upload_path), exist_ok=True)
                form.profile_picture.data.save(upload_path)
                profile.profile_picture = filename

            # Handle cover photo upload
            if form.cover_photo.data and hasattr(form.cover_photo.data, 'filename'):
                filename = secure_filename(form.cover_photo.data.filename)
                upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                os.makedirs(os.path.dirname(upload_path), exist_ok=True)
                form.cover_photo.data.save(upload_path)
                profile.cover_photo = filename

            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('view_profile', profile_id=profile.id))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')

    # Pre-fill the timeline events field with JSON data
    form.timeline_events.data = json.dumps(profile.timeline_events)

    return render_template('edit_profile.html', form=form, profile=profile)

@app.route('/delete_profile/<int:profile_id>', methods=['POST'])
@login_required
def delete_profile(profile_id):
    profile = Profile.query.get_or_404(profile_id)
    if profile.user_id != current_user.id:
        flash('You do not have permission to delete this profile.', 'danger')
        return redirect(url_for('dashboard'))
    
    try:
        db.session.delete(profile)
        db.session.commit()
        flash('Profile deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')
    
    return redirect(url_for('dashboard'))

@app.route('/api/profile/<int:profile_id>/timeline')
@login_required
def api_profile_timeline(profile_id):
    try:
        profile = Profile.query.get_or_404(profile_id)
        if profile.user_id != current_user.id:
            return jsonify({"error": "Unauthorized"}), 403

        timeline_events = [
            {
                "date": timeline.date.strftime('%Y-%m-%d'),
                "event": timeline.event
            } for timeline in profile.timelines
        ]
        return jsonify(timeline_events)
    except Exception as e:
        app.logger.error(f"Error fetching timeline: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/components/<path:filename>')
def serve_component(filename):
    if filename.endswith('.js'):
        return send_from_directory(os.path.join(app.root_path, 'static/components'), filename, mimetype='application/javascript')
    return send_from_directory(os.path.join(app.root_path, 'static/components'), filename)

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = SettingsForm()
    if form.validate_on_submit():
        user = User.query.get(current_user.id)
        
        # Check if the current password is correct
        if not check_password_hash(user.password, form.current_password.data):
            flash('Current password is incorrect.', 'danger')
            return redirect(url_for('settings'))
        
        # Update email
        user.email = form.email.data
        
        # Update password if provided
        if form.new_password.data:
            user.password = generate_password_hash(form.new_password.data, method='pbkdf2:sha256')
        
        db.session.commit()
        flash('Your settings have been updated!', 'success')
        return redirect(url_for('dashboard'))
    
    elif request.method == 'GET':
        form.email.data = current_user.email
    
    return render_template('settings.html', form=form)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')    

@app.route('/faq')
def faq():
    return render_template('faq.html')  

@app.route('/disclaimer')
def disclaimer():
    return render_template('disclaimer.html')      

@app.route('/imortis')
def imortis():
    return render_template('imortis.html')

# Run the app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables for our data models
    app.run(host='0.0.0.0', port=5000)