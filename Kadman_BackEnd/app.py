from vendors import vendors_bp
from waiting_vendors import waiting_vendors_bp
from layouts import layouts_bp
from flask import Flask
from flask_cors import CORS
import os
import mysql.connector
from verification import verification_bp


def create_app():
    print('connecting to the database')
    app = Flask(__name__)
    CORS(app,supports_credentials=True)
    try:
        connection = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DB"),
            port=int(os.getenv("MYSQL_PORT", 3306))
        )
        print("MySQL connection established")
    except Exception as e:
        print("MySQL connection error:", e)

    app.db = connection

    app.register_blueprint(vendors_bp)
    app.register_blueprint(waiting_vendors_bp)
    app.register_blueprint(layouts_bp)
    app.register_blueprint(verification_bp)
    # app.register_blueprint(payment_bp, url_prefix='/payment')

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True,port=8080)
