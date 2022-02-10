from flask import Flask
from flask_cors import CORS

app = Flask(__name__, static_folder='react-flask-app/build', static_url_path='')
cors = CORS(app)

from app import routes
