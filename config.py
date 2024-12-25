import os
class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "addsecretkeyhere"
    FLASK_APP =  'app'
    SQLALCHEMY_DATABASE_URI = "sqlite:///fsm.sqlite3"
