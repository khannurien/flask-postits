from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, URL


class LoginForm(FlaskForm):
    nickname = StringField("Identifiant", validators=[DataRequired()])
    password = PasswordField("Mot de passe", validators=[DataRequired()])
    submit = SubmitField("Connexion")


class NewPostitForm(FlaskForm):
    url = StringField("URL", validators=[DataRequired(), URL()])
    content = StringField("Petit mot", validators=[DataRequired()])
    submit = SubmitField("Envoyer")
