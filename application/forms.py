from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired
from wtforms import FileField, StringField
from wtforms.validators import DataRequired


class UploadForm(FlaskForm):

    cpo_zip_file = FileField(validators=[FileRequired()])


class SearchForm(FlaskForm):

    query = StringField('Enter your search', validators=[DataRequired()])