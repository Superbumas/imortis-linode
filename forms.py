from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, FileField, SubmitField
from wtforms.validators import DataRequired, Length

class ProfileForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    bio = TextAreaField('Bio', validators=[DataRequired()])
    date_of_birth = DateField('Date of Birth', format='%Y-%m-%d', validators=[DataRequired()])
    date_of_death = DateField('Date of Death', format='%Y-%m-%d', validators=[DataRequired()])
    profile_picture = FileField('Profile Picture')
    submit = SubmitField('Create Profile')

class DeleteProfileForm(FlaskForm):
    submit = SubmitField('Delete')