from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, NumberRange
import sqlalchemy as sa
from app import db
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()], description='Ваш логин')
    password = PasswordField('Пароль', validators=[DataRequired()], description='Ваш пароль')
    remember_me = BooleanField('Запомнить')
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()], description='Новый логин')
    email = StringField('Email', validators=[DataRequired(), Email()], description='Ваша почта')
    password = PasswordField('Пароль', validators=[DataRequired()], description='Новый пароль')
    password2 = PasswordField(
        'Повторите пароль', validators=[DataRequired(), EqualTo('password')], description='Повторите праоль')
    submit = SubmitField('Зарегистрироваться')

    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(
            User.username == username.data))
        if user is not None:
            raise ValidationError('Логин уже занят, попробуйте другой вариант.')

    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(
            User.email == email.data))
        if user is not None:
            raise ValidationError('Почта уже зарегистрирована, попробуйте использовать другую почту.')

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('Обо мне', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')


class RatingForm(FlaskForm):
    score = IntegerField('Оценка (от 1 до 5)', validators=[DataRequired(), NumberRange(min=1, max=5)])
    submit = SubmitField('Оценить')


class CommentForm(FlaskForm):
    text = TextAreaField('Комментарий', validators=[DataRequired()])
    submit = SubmitField('Отправить')