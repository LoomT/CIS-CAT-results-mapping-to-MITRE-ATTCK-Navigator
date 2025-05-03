import os
import time

from flask import Flask, send_from_directory
from flask.cli import load_dotenv

load_dotenv()
app = Flask(__name__, static_folder=os.getenv('FLASK_STATIC_FOLDER'), static_url_path='/')

@app.route('/api/time')
def get_current_time():
    return {'time': time.time()}

# Serve React App
@app.route('/')
def serve():
    print('connecting')
    return send_from_directory(app.static_folder, 'index.html')


if __name__ == '__main__':
    app.run()
