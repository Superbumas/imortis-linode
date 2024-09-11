from flask import Flask, render_template, redirect, url_for, flash, jsonify, request, session, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, PasswordField, DateField, FileField, FieldList, FormField
from wtforms.validators import DataRequired, Length, ValidationError, EqualTo, Email
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import qrcode
from datetime import datetime
from forms import DeleteProfileForm, ProfileForm, EditProfileForm, EditTimelineForm
import os
import base64
import logging
import io
from forms import DeleteProfileForm, ProfileForm, EditProfileForm, EditTimelineForm
from flask_wtf.file import FileField, FileAllowed, FileRequired



# Flask app configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = 'ThisIsASecretKey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)  # Add this line
    password = db.Column(db.String(255), nullable=False)

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    profile_picture = db.Column(db.String(100), nullable=True)
    cover_photo = db.Column(db.String(100), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=False)
    date_of_death = db.Column(db.Date, nullable=True)
    country = db.Column(db.String(50), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    timeline_events = db.relationship('TimelineEvent', backref='profile', lazy=True, cascade="all, delete-orphan")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    def __repr__(self):
        return f'<Profile {self.name}>'

class TimelineEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profile.id'), nullable=False)
    event_date = db.Column(db.Date, nullable=False)
    event_text = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Remove the back_populates to avoid conflict
    # profile = db.relationship('Profile', back_populates='timeline_events')

# Forms
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class TimelineForm(FlaskForm):
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    event = StringField('Event', validators=[DataRequired(), Length(max=255)])

class SettingsForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_new_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Update Settings')

class DeleteProfileForm(FlaskForm):
    submit = SubmitField('Delete')

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
    form = ProfileForm()
    if form.validate_on_submit():
        try:
            profile_picture = None
            if form.profile_picture.data:
                filename = secure_filename(form.profile_picture.data.filename)
                upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                os.makedirs(os.path.dirname(upload_path), exist_ok=True)
                form.profile_picture.data.save(upload_path)
                profile_picture = filename

            cover_photo = None
            if form.cover_photo.data:
                filename = secure_filename(form.cover_photo.data.filename)
                upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                os.makedirs(os.path.dirname(upload_path), exist_ok=True)
                form.cover_photo.data.save(upload_path)
                cover_photo = filename

            profile = Profile(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                bio=form.bio.data,
                profile_picture=profile_picture,
                cover_photo=cover_photo,
                date_of_birth=form.date_of_birth.data,
                date_of_death=form.date_of_death.data if form.date_of_death.data else None,
                country=form.country.data,
                city=form.city.data,
                user_id=current_user.id,
            )
            db.session.add(profile)
            db.session.commit()
            flash('Profile created successfully!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
    return render_template('create_profile.html', form=form)

@app.route('/profile/<int:profile_id>', methods=['GET'])
def view_profile(profile_id):
    profile = db.session.get(Profile, profile_id)
    if profile is None:
        flash('Profile not found.', 'danger')
        return redirect(url_for('dashboard'))
    
    if current_user.is_authenticated:
        delete_form = DeleteProfileForm()
        return render_template('view_profile.html', profile=profile, form=delete_form)
    else:
        return render_template('view_profile_public.html', profile=profile)


@app.route('/profile/edit/<int:profile_id>', methods=['GET', 'POST'])
@login_required
def edit_profile(profile_id):
    profile = db.session.get(Profile, profile_id)
    if profile is None:
        flash('Profile not found.', 'danger')
        return redirect(url_for('dashboard'))
    
    form = EditProfileForm(obj=profile)
        # Populate timeline_events with existing events or at least one empty entry
    if request.method == 'GET':
        for event in profile.timeline_events:
            form.timeline_events.append_entry({
                'event_date': event.event_date,
                'event_text': event.event_text
            })
        if not profile.timeline_events:
            form.timeline_events.append_entry()
    if form.validate_on_submit():
        try:
            profile.first_name = form.first_name.data
            profile.last_name = form.last_name.data
            profile.bio = form.bio.data

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

            profile.date_of_birth = form.date_of_birth.data
            profile.date_of_death = form.date_of_death.data
            profile.country = form.country.data
            profile.city = form.city.data

            # Clear existing timeline events
            TimelineEvent.query.filter_by(profile_id=profile.id).delete()

            # Add new timeline events
            for event_form in form.timeline_events.entries:
                event = TimelineEvent(
                    event_date=event_form.event_date.data,
                    event_text=event_form.event_text.data,
                    profile_id=profile.id
                )
                profile.timeline_events.append(event)

            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('view_profile', profile_id=profile.id))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
    
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


@app.route('/api/profiles')
@login_required
def api_profiles():
    try:
        profiles = Profile.query.filter_by(user_id=current_user.id).all()
        profiles_data = [
            {
                "id": profile.id,
                "name": profile.name,
                "bio": profile.bio,
                "date_of_birth": profile.date_of_birth.strftime('%Y-%m-%d'),
                "date_of_death": profile.date_of_death.strftime('%Y-%m-%d'),
                "timelines": [
                    {
                        "date": timeline.date.strftime('%Y-%m-%d'),
                        "event": timeline.event
                    } for timeline in profile.timelines
                ]
            } for profile in profiles
        ]
        return jsonify(profiles_data)
    except Exception as e:
        app.logger.error(f"Error fetching profiles: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

# Utility functions
def generate_qr(data, filename):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    
    # Ensure the directory exists
    qr_code_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'qr_codes')
    os.makedirs(qr_code_dir, exist_ok=True)
    
    # Save the image
    file_path = os.path.join(qr_code_dir, filename)
    img.save(file_path)
    
    return file_path

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
    app.run(host='0.0.0.0', port=5000)
    
# Create database tables
with app.app_context():
    db.create_all()