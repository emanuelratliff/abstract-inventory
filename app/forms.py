from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, \
    SubmitField, SelectField, IntegerField, RadioField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import User, Admin, Users, Monitors, Desktop, Laptop, Printer, Scanner, Toner, Other, CheckOut
from app import app, db

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.') 

class EditProfileForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_email, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_email = original_email
    def validate_email(self, email):
        if email.data != self.original_email:
            email = User.query.filter_by(email=email.data).first()
            if email is not None:
                raise ValidationError('Please use a different email address!')

class AdminUserForm(FlaskForm):
    select_field = SelectField(u'Users', coerce=int)
    radio_field = RadioField('Actions', choices=[('option1', 'Make Admin'),
                                                 ('option2', 'Remove Admin'),
                                                 ('option3', 'Delete User')])
    submit = SubmitField('Submit')

class ImportUserForm(FlaskForm):
    employee_id = StringField('Employee ID', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    room_number = StringField('Room Number', validators=[DataRequired()])
    monitor_serial_number1 = StringField('Monitor 1 Serial Number')
    monitor_asset_tag1 = StringField('Monitor 1 Asset Tag')
    monitor_serial_number2 = StringField('Monitor 2 Serial Number')
    monitor_asset_tag2 = StringField('Monitor 2 Asset Tag')
    desktop_name = StringField('Desktop Name')
    desktop_serial_number = StringField('Desktop Serial Number')
    desktop_asset_tag = StringField('Desktop Asset Tag')
    laptop_name = StringField('Laptop Name')
    laptop_serial_number = StringField('Laptop Serial Number')
    laptop_asset_tag = StringField('Laptop Asset Tag')
    printer_model = StringField('Printer Model')
    printer_serial_number = StringField('Printer Serial Number')
    printer_asset_tag = StringField('Printer Asset Tag')
    scanner_model = StringField('Scanner Model')
    scanner_serial_number = StringField('Scanner Serial Number')
    scanner_asset_tag = StringField('Scanner Asset Tag')
    submit = SubmitField('Submit')

    # Since the employee ID is the primary key, I wanted to ensure you could not put the same
    # employee ID for another user.
    def validate_employee_id(self, employee_id):
        employee_id = Users.query.filter_by(employee_id=employee_id.data).first()
        if employee_id:
            raise ValidationError('Please use a different employee code or id.')

class SearchUserForm(FlaskForm):
    search = StringField('Username')
    submit = SubmitField('Search')

class EditImportForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    room_number = StringField('Room Number', validators=[DataRequired()])
    monitor_serial_number1 = StringField('Monitor 1 Serial Number')
    monitor_asset_tag1 = StringField('Monitor 1 Asset Tag')
    monitor_serial_number2 = StringField('Monitor 2 Serial Number')
    monitor_asset_tag2 = StringField('Monitor 2 Asset Tag')
    desktop_name = StringField('Desktop Name')
    desktop_serial_number = StringField('Desktop Serial Number')
    desktop_asset_tag = StringField('Desktop Asset Tag')
    laptop_name = StringField('Laptop Name')
    laptop_serial_number = StringField('Laptop Serial Number')
    laptop_asset_tag = StringField('Laptop Asset Tag')
    printer_model = StringField('Printer Model')
    printer_serial_number = StringField('Printer Serial Number')
    printer_asset_tag = StringField('Printer Asset Tag')
    scanner_model = StringField('Scanner Model')
    scanner_serial_number = StringField('Scanner Serial Number')
    scanner_asset_tag = StringField('Scanner Asset Tag')
    submit = SubmitField('Submit')

class InventoryForm(FlaskForm):
    other_item_name = StringField('Item Name', validators=[DataRequired()])
    other_serial_number = StringField('Item Serial Number')
    other_asset_tag = StringField('Item Asset Tag')
    submit = SubmitField('Submit')

class CheckOutForm(FlaskForm):
    select_field = SelectField(u'Users', coerce=int)
    checkout_asset_tag = StringField('Item Asset Tag', validators=[DataRequired()])
    submit = SubmitField('Check Out')

class TonerForm(FlaskForm):
    toner_model = StringField('Toner Model', validators=[DataRequired()])
    toner_cartridge = StringField('Toner Cartridge', validators=[DataRequired()])
    toner_color = StringField('Toner Color')
    toner_quantity = IntegerField('Quantity')
    submit = SubmitField('Submit')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')