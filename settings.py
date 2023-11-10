from os import getenv
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = getenv('SECRET_KEY')
ALGORITHM = getenv('ALGORITHM')
SQLALCHEMY_DATABASE_URL = getenv('SQLALCHEMY_DATABASE_URL')