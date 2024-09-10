from flask_wtf import FlaskForm
from wtforms import SubmitField

class DeleteProfileForm(FlaskForm):
    submit = SubmitField('Delete')