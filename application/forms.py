from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired
from wtforms import FileField


class UploadForm(FlaskForm):

    cpo_zip_file = FileField(validators=[FileRequired()])