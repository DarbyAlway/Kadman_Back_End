from vendors import vendors_bp
from waiting_vendors import waiting_vendors_bp
from layouts import layouts_bp
from flask import Flask
from flask_cors import CORS
import os
import mysql.connector


def create_app():
    app = Flask(__name__)
    CORS(app,supports_credentials=True)

    connection = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DB"),
        port=int(os.getenv("MYSQL_PORT", 3306))
    )

    app.db = connection

    app.register_blueprint(vendors_bp)
    app.register_blueprint(waiting_vendors_bp)
    app.register_blueprint(layouts_bp)
    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
