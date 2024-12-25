from flask_wtf import FlaskForm
from wtforms import EmailField, StringField, PasswordField, SubmitField, DateField, SelectField, ValidationError
from wtforms.validators import DataRequired, EqualTo
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')


class SignupForm(FlaskForm):
    username = StringField('Username',  validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    email    = EmailField("Email", validators=[DataRequired()])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        existing_user = User.query.filter_by(username=username.data).first()
        if existing_user:
            raise ValidationError('This username is already taken. Please choose a different one.')


class CategoryForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    value = StringField('Value', validators=[DataRequired()])
    exp_type = SelectField("Expense Type",
        choices=[
                ("spent","Spent"),
                ("earned","Earned")
            ],validators=[DataRequired()])
    submit = SubmitField('Submit')

class EditCategory(FlaskForm):
    name = StringField('Edit Name', validators=[DataRequired()])
    value = StringField('Edit Value', validators=[DataRequired()])
    addval = StringField("Add to Value")
    exp_type = SelectField(
        "Expense Type",
        choices=[
                ("spent","Spent"),
                ("earned","Earned")
                ],validators=[DataRequired()])
    submit = SubmitField('Submit')

class TargetForm(FlaskForm):
    name = SelectField(
        "Target Name",
        choices=[
        ],
    validators=[DataRequired() ])
    value = StringField('Target Amount', validators=[DataRequired()])
    date = DateField('Target Date', format='%Y-%m-%d')
    submit = SubmitField('Submit')
