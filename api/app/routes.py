from app import app, cors
from flask_cors import cross_origin
import time

@app.route('/')
@cross_origin()
def serve():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/time')
@cross_origin()
def get_current_time():
    return {'time': time.time()}
