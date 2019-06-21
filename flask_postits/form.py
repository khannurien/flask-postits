from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, URL


class LoginForm(FlaskForm):
    nickname = StringField("Identifiant", validators=[DataRequired()])
    password = PasswordField("Mot de passe", validators=[DataRequired()])
    submit = SubmitField("Connexion")

class SignupForm(FlaskForm):
    nickname = StringField("Identifiant", validators=[DataRequired()])
    name = StringField("Nom (optionnel)")
    password = PasswordField("Mot de passe", validators=[DataRequired(), EqualTo('password_confirm')])
    password_confirm = PasswordField("Mot de passe (confirmation)", validators=[DataRequired()])
    submit = SubmitField("Inscription")

class NewPostitForm(FlaskForm):
    url = StringField("URL", validators=[DataRequired(), URL()])
    content = StringField("Petit mot", validators=[DataRequired(), Length(max=240)])
    submit = SubmitField("Envoyer")
