from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, DateField, FieldList, FormField, FileField, PasswordField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_wtf.file import FileField, FileAllowed





# List of countries
COUNTRIES = [
    ('US', 'United States'), ('CA', 'Canada'), ('MX', 'Mexico'), 
    # Add more countries as needed
    ('GB', 'United Kingdom'), ('FR', 'France'), ('DE', 'Germany'), 
    ('IN', 'India'), ('CN', 'China'), ('JP', 'Japan')
    # You can add a comprehensive list of countries here
]

class ProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    bio = TextAreaField('Bio', validators=[Length(max=500)])
    profile_picture = FileField('Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    cover_photo = FileField('Cover Photo', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    date_of_birth = DateField('Date of Birth', format='%d-%m-%Y', validators=[DataRequired()])
    date_of_death = DateField('Date of Death', format='%d-%m-%Y', validators=[DataRequired()])
    country = StringField('Country', validators=[DataRequired(), Length(max=50)])
    city = StringField('City', validators=[DataRequired(), Length(max=50)])
    submit = SubmitField('Create Profile')

class TimelineEventForm(FlaskForm):
    event_date = DateField('Event Date', format='%Y-%m-%d', validators=[DataRequired()])
    event_text = StringField('Event Text', validators=[DataRequired()])

class EditProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    bio = TextAreaField('Bio', validators=[Length(max=500)])
    date_of_birth = DateField('Date of Birth', format='%d-%m-%Y', validators=[DataRequired()])
    date_of_death = DateField('Date of Death', format='%d-%m-%Y', validators=[DataRequired()])
    country = StringField('Country', validators=[DataRequired(), Length(max=50)])
    city = StringField('City', validators=[DataRequired(), Length(max=50)])
    profile_picture = FileField('Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    cover_photo = FileField('Cover Photo', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    timeline_events = FieldList(FormField(TimelineEventForm), min_entries=0)
    submit = SubmitField('Save')

class EditTimelineForm(FlaskForm):
    timeline_events = FieldList(FormField(TimelineEventForm), min_entries=1)
    submit = SubmitField('Save Changes')    

class DeleteProfileForm(FlaskForm):
    submit = SubmitField('Delete')

    # Forms
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        from models import User  # Local import to avoid circular import
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class SettingsForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_new_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Update Settings')

class DeleteProfileForm(FlaskForm):
    submit = SubmitField('Delete')