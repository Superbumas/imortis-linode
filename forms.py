from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, FileField, SubmitField
from wtforms.validators import DataRequired, Length

# List of countries
COUNTRIES = [
    ('US', 'United States'), ('CA', 'Canada'), ('MX', 'Mexico'), 
    # Add more countries as needed
    ('GB', 'United Kingdom'), ('FR', 'France'), ('DE', 'Germany'), 
    ('IN', 'India'), ('CN', 'China'), ('JP', 'Japan')
    # You can add a comprehensive list of countries here
    
class ProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    bio = TextAreaField('Bio', validators=[Optional()])
    profile_picture = FileField('Profile Picture', validators=[Optional()])
    cover_photo = FileField('Cover Photo', validators=[Optional()])
    email = StringField('Email', validators=[Optional()])
    country = SelectField('Country', choices=COUNTRIES, validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    submit = SubmitField('Create Profile')

class DeleteProfileForm(FlaskForm):
    submit = SubmitField('Delete')