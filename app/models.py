from datetime import datetime
from hashlib import md5
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import app, db, login
from time import time
import jwt

# User class to allow access into the Inventory System. The avatar function is the
# only function that pulls from an external website.
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    admins = db.relationship('Admin', backref='admin_username', lazy='dynamic', cascade='all,delete-orphan')


    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

# decorator used to load the user into the application.
@login.user_loader
def load_user(id):
    return User.query.get(int(id))

# Admin class which gives the rights to make other users admins, remove them from
# admin group, and also delete them from the system completely.
class Admin(db.Model):
    def __init__(self, user, admin_username):
        self.user = user
        self.admin_username = admin_username

    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __repr__(self):
        return '<Admin {}>'.format(self.user)

    # These functions allow the admin to delete a specified user from the database and all the items attached
    # to their name. The admin account can also delete other admins and users. A word of caution,
    # do not try to delete a user if they have items checked out to their name.
    def delete_user(self, name):
        db.session.delete(User.query.filter_by(username=name.username).first())
        db.session.commit()

    def delete_admin(self, name):
        db.session.delete(Admin.query.filter_by(user=name.username).first())
        db.session.commit()

    def delete_users(self, name):
        db.session.delete(Users.query.filter_by(username=name.username).first())
        db.session.commit()

    def delete_item(self, name):
        db.session.delete(Other.query.filter_by(other_item_name=name.other_item_name).first())
        db.session.commit()

    def delete_toners(self, name):
        db.session.delete(Toner.query.filter_by(toner_cartridge=name.toner_cartridge).first())
        db.session.commit()

# These classes are used in conjunction with the ImportUserForm and allows the creation
# of users in the system.
class Users(db.Model):
    employee_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    email = db.Column(db.String(120), index=True, unique=True)
    room_number = db.Column(db.String(5))
    monitors = db.relationship('Monitors', backref='monitor_id', lazy='dynamic', cascade='all,delete-orphan')
    desktop = db.relationship('Desktop', backref='desktop_id', lazy='dynamic', cascade='all, delete-orphan')
    laptop = db.relationship('Laptop', backref='laptop_id', lazy='dynamic', cascade='all, delete-orphan')
    printer = db.relationship('Printer', backref='printer_id', lazy='dynamic', cascade='all, delete-orphan')
    scanner = db.relationship('Scanner', backref='scanner_id', lazy='dynamic', cascade='all, delete-orphan')


    def __repr__(self):
        return '<Users {}>'.format(self.username)



class Monitors(db.Model):
    def __init__(self, monitor_serial_number, monitor_asset_tag, monitor_id):
        self.monitor_serial_number = monitor_serial_number
        self.monitor_asset_tag = monitor_asset_tag
        self.monitor_id = monitor_id

    monitors_id = db.Column(db.Integer, primary_key=True)
    monitor_serial_number = db.Column(db.String(40))
    monitor_asset_tag = db.Column(db.String(40))
    monitor_reference_id = db.Column(db.Integer, db.ForeignKey('users.employee_id'))

    def __repr__(self):
        return '<Monitor {}>'.format(self.monitor_serial_number)


class Desktop(db.Model):
    def __init__(self, desktop_name, desktop_serial_number, desktop_asset_tag, desktop_id):
        self.desktop_name = desktop_name
        self.desktop_serial_number = desktop_serial_number
        self.desktop_asset_tag = desktop_asset_tag
        self.desktop_id = desktop_id

    desktops_id = db.Column(db.Integer, primary_key=True)
    desktop_name = db.Column(db.String(40))
    desktop_serial_number = db.Column(db.String(40))
    desktop_asset_tag = db.Column(db.String(40))
    desktop_reference_id = db.Column(db.Integer, db.ForeignKey('users.employee_id'))

    def __repr__(self):
        return '<Desktop {}>'.format(self.desktop_name)


class Laptop(db.Model):
    def __init__(self, laptop_name, laptop_serial_number, laptop_asset_tag, laptop_id):
        self.laptop_name = laptop_name
        self.laptop_serial_number = laptop_serial_number
        self.laptop_asset_tag = laptop_asset_tag
        self.laptop_id = laptop_id

    laptops_id = db.Column(db.Integer, primary_key=True)
    laptop_name = db.Column(db.String(40))
    laptop_serial_number = db.Column(db.String(40))
    laptop_asset_tag = db.Column(db.String(40))
    laptop_reference_id = db.Column(db.Integer, db.ForeignKey('users.employee_id'))

    def __repr__(self):
        return '<Laptop {}>'.format(self.laptop_serial_number)


class Printer(db.Model):
    def __init__(self, printer_model, printer_serial_number, printer_asset_tag, printer_id):
        self.printer_model = printer_model
        self.printer_serial_number = printer_serial_number
        self.printer_asset_tag = printer_asset_tag
        self.printer_id = printer_id

    printers_id = db.Column(db.Integer, primary_key=True)
    printer_model = db.Column(db.String(40))
    printer_serial_number = db.Column(db.String(40))
    printer_asset_tag = db.Column(db.String(40))
    printer_reference_id = db.Column(db.Integer, db.ForeignKey('users.employee_id'))

    def __repr__(self):
        return '<Printer {}>'.format(self.printer_model)


class Scanner(db.Model):
    def __init__(self, scanner_model, scanner_serial_number, scanner_asset_tag, scanner_id):
        self.scanner_model = scanner_model
        self.scanner_serial_number = scanner_serial_number
        self.scanner_asset_tag = scanner_asset_tag
        self.scanner_id = scanner_id

    scanners_id = db.Column(db.Integer, primary_key=True)
    scanner_model = db.Column(db.String(40))
    scanner_serial_number = db.Column(db.String(40))
    scanner_asset_tag = db.Column(db.String(40))
    scanner_reference_id = db.Column(db.Integer, db.ForeignKey('users.employee_id'))

    def __repr__(self):
        return '<Scanner {}>'.format(self.scanner_model)

class Toner(db.Model):
    def __init__(self, toner_model, toner_cartridge, toner_color, toner_quantity):
        self.toner_model = toner_model
        self.toner_cartridge = toner_cartridge
        self.toner_color = toner_color
        self.toner_quantity = toner_quantity

    toner_id = db.Column(db.Integer, primary_key=True)
    toner_model = db.Column(db.String(40))
    toner_cartridge = db.Column(db.String(40))
    toner_color = db.Column(db.String(40))
    toner_quantity = db.Column(db.Integer)

    def __repr__(self):
        return '<Toner {}>'.format(self.toner_model)

# This class is primarily used for the Checkout system.
class Other(db.Model):
    def __init__(self, other_item_name, other_serial_number, other_asset_tag):
        self.other_item_name = other_item_name
        self.other_serial_number = other_serial_number
        self.other_asset_tag = other_asset_tag

    others_id = db.Column(db.Integer, primary_key=True)
    other_item_name = db.Column(db.String(40))
    other_serial_number = db.Column(db.String(40))
    other_asset_tag = db.Column(db.String(40))

    def __repr__(self):
        return '<Other {}>'.format(self.other.item_name)

# This class is used to checkout items in the Other class.
class CheckOut(db.Model):
    def __init__(self, checkout_timestamp, checkout_username, checkout_item_name, checkout_serial_number,
                 checkout_asset_tag):
        self.checkout_timestamp = checkout_timestamp
        self.checkout_username = checkout_username
        self.checkout_item_name = checkout_item_name
        self.checkout_serial_number = checkout_serial_number
        self.checkout_asset_tag = checkout_asset_tag

    check_out_id = db.Column(db.Integer, primary_key=True)
    checkout_timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    checkout_username = db.Column(db.String(40))
    checkout_item_name = db.Column(db.String(40))
    checkout_serial_number = db.Column(db.String(40))
    checkout_asset_tag = db.Column(db.String(40))

    def __repr__(self):
        return '<CheckOut {}>'.format(self.checkout_username)

