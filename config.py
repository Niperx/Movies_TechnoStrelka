import os
basedir = os.path.abspath(os.path.dirname(__file__))
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'sqlite:///' + os.path.join(basedir, 'db/main.db')
    kp_API_KEY = '89833804-3dc2-4fac-9d08-a0603f43c874' # Кинопоиск
    openAI_API_KEY = "sk-MsYz8DlX7XHgtxT4fifxj3RVfvUWOb1D"