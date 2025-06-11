from vendors import vendors_bp
from waiting_vendors import waiting_vendors_bp
from layouts import layouts_bp
from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app,supports_credentials=True)
    app.register_blueprint(vendors_bp)
    app.register_blueprint(waiting_vendors_bp)
    app.register_blueprint(layouts_bp)
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)