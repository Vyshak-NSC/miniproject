from flask import Flask
from flask_cors import CORS
from app.models import User
from .extensions import db, login_manager

app = Flask(__name__)
CORS(app)
app.config.from_object("config.Config")  

db.init_app(app)
login_manager.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'index'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


from app import routes,models
