from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, StringField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileRequired, FileAllowed

cat_names = ['Alligator',
             'Apollo',
             'Armadillo',
             'Campus Cat #4',
             'Dog',
             'Raccoon',
             'Ryan the Engineering Cat',
             'Tenders',
             'Other'
             ]


class markerForm(FlaskForm):
    other = StringField(label='Please list animal if not listed')
    cats = SelectField(label='Animal', choices=cat_names, validators=[DataRequired()])
    doc = FileField('Upload Document', validators=[FileAllowed(['png', 'jpeg', 'jpg'], 'PNG, JPG, or JPEG only!')])
    submit = SubmitField('Enter')
