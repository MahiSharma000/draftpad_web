# -*- encoding: utf-8 -*-
from flask_migrate import Migrate
from sys import exit
from decouple import config

from apps.config import config_dict
from apps import create_app, db
#import firebase_admin
#from firebase_admin import credentials
#from firebase_admin import messaging

#cred = credentials.Certificate(r"C:\Users\ortha\Videos\secret.json")
#firebase_admin.initialize_app(cred)
print("Initialized Cloud messaging")
DEBUG = config('DEBUG', default=True, cast=bool)

get_config_mode = 'Debug' if DEBUG else 'Production'

try:
    # Load the configuration using the default values
    app_config = config_dict[get_config_mode.capitalize()]

except KeyError: 
    exit('Error: Invalid <config_mode>. Expected values [Debug, Production] ') 

app = create_app(app_config)
Migrate(app, db)

if DEBUG:
    app.logger.info('DEBUG       = ' + str(DEBUG))
    app.logger.info('Environment = ' + get_config_mode)
    app.logger.info('DBMS        = ' + app_config.SQLALCHEMY_DATABASE_URI)

if __name__ == "__main__":
    # create the tables if they don't exist
    
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0')
