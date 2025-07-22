from flask import Flask 
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
pharmbook_init = Flask(__name__)
pharmbook_init.config.from_object(Config)
pharmbook_init.config['SECRET_KEY'] = Config.SECRET_KEY
db=SQLAlchemy(pharmbook_init)
migrate = Migrate(pharmbook_init, db)
login=LoginManager(pharmbook_init)
login.login_view = 'login'



from pharmbook_app import routes 
