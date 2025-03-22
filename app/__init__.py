from flask import Flask
from flask_session import Session

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '6006'
    app.config['SESSION_TYPE'] = 'filesystem'
    Session(app)

    from .routes import main
    app.register_blueprint(main)

    return app