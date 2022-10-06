from flask_wtf import FlaskForm
from wtforms import StringField
class formEstudiante(FlaskForm):
    documento = StringField("Documento Identidad")