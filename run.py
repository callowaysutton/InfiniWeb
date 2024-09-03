# Start a Gunicorn server with the Flask app
from app import app
from app.models import db
import os

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(port=5005, threaded=True)