import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask import Flask, request, current_app
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment

# This is used to tell Flask where to look for the static folders
app = Flask(__name__, static_url_path="/inventory/static", static_folder=os.path.abspath("static/"))
# This is for your config file
app.config.from_object(Config)
# Instantiates the database object
db = SQLAlchemy(app)
# Instantiates the migration object
migrate = Migrate(app, db)
# Instantiates the login object and view
login = LoginManager(app)
login.login_view = 'login'
# Instantiates the mail object for your mail server
mail = Mail(app)
# Instantiates the bootstrap object so it can be used throughout your templates
bootstrap = Bootstrap(app)
# Although I already have a parameter for this in my config file, I decided to give it a value in the
# init.py module. This allows me to see changes within my templates without clearing the cache files
# in my browser
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
# Instantiates the moment object from the moment.js module
moment = Moment(app)

# Used to build your Mail server to send passwords to your users
if not app.debug:
        if app.config['MAIL_SERVER']:            
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])                                     
            secure = None
            if app.config['MAIL_USE_TLS']:                                                                
                secure = ()                                                                    
            mail_handler = SMTPHandler(
                    mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                    fromaddr='no-reply@' + app.config['MAIL_SERVER'],   
                    toaddrs=app.config['ADMINS'], subject='MIS Inventory Failure',
                    credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)
        # This is for building your logs
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/inventory.log', maxBytes=10240,
                                           backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('IT Inventory DB startup')

# Used for circular dependency
from app import routes, models, errors, tables
