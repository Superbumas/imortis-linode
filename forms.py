from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, FileField, SubmitField, FieldList, FormField
from wtforms.validators import DataRequired, Length, Optional
from wtforms.fields import SelectField

# List of countries
COUNTRIES = [
    ('US', 'United States'), ('CA', 'Canada'), ('MX', 'Mexico'), 
    # Add more countries as needed
    ('GB', 'United Kingdom'), ('FR', 'France'), ('DE', 'Germany'), 
    ('IN', 'India'), ('CN', 'China'), ('JP', 'Japan')
    # You can add a comprehensive list of countries here
]

class TimelineEventForm(FlaskForm):
    event_date = DateField('Event Date', validators=[DataRequired()])
    event_text = TextAreaField('Event Text', validators=[DataRequired()])

class ProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    bio = TextAreaField('Bio', validators=[Optional()])
    profile_picture = FileField('Profile Picture', validators=[Optional()])
    cover_photo = FileField('Cover Photo', validators=[Optional()])
    date_of_birth = DateField('Date of Birth', format='%Y-%m-%d', validators=[DataRequired()])
    date_of_death = DateField('Date of Death', format='%Y-%m-%d', validators=[DataRequired()])
    country = SelectField('Country', choices=COUNTRIES, validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    submit = SubmitField('Create Profile')

class DeleteProfileForm(FlaskForm):
    submit = SubmitField('Delete')

class EditProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    bio = TextAreaField('Bio', validators=[Optional()])
    profile_picture = FileField('Profile Picture', validators=[Optional()])
    cover_photo = FileField('Cover Photo', validators=[Optional()])
    date_of_birth = DateField('Date of Birth', format='%Y-%m-%d', validators=[DataRequired()])
    date_of_death = DateField('Date of Death', format='%Y-%m-%d', validators=[DataRequired()])
    country = SelectField('Country', choices=COUNTRIES, validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    submit = SubmitField('Save Changes')

class EditTimelineForm(FlaskForm):
    timeline_events = FieldList(FormField(TimelineEventForm), min_entries=1)
    submit = SubmitField('Save Changes')    

