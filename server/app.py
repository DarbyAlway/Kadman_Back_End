from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from routes.vendors import vendors_bp
from routes.layouts import layouts_bp
from routes.verification import verification_bp
from routes.webhook import webhook_bp
import mysql.connector
import os

load_dotenv()


def create_app():
    app = Flask(__name__)
    CORS(app, supports_credentials=True)

    try:
        connection = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DB"),
            port=int(os.getenv("MYSQL_PORT", 3306))
        )
        print("MySQL connection established")
        app.db = connection
    except Exception as e:
        print("MySQL connection error:", e)
        app.db = None

    app.register_blueprint(vendors_bp)
    app.register_blueprint(layouts_bp)
    app.register_blueprint(verification_bp)
    app.register_blueprint(webhook_bp)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
