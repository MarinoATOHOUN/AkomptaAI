import os
import sys

# Ajouter le répertoire parent (akompta_backend) au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

# Initialisation de l\"application Flask
app = Flask(__name__, static_folder="./static", static_url_path="/")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///akompta.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "super_secret_key")

CORS(app)  # Activer CORS pour toutes les routes

db = SQLAlchemy(app)

# Importation des modèles après la création de db
from src.models.user import User
from src.models.product import Product
from src.models.sale import Sale
from src.models.expense import Expense
from src.models.savings import Savings
from src.models.stock_movement import StockMovement
from src.models.report import Report

# Création des tables de la base de données
with app.app_context():
    db.create_all()

# Enregistrement des blueprints
from src.routes.auth import auth_bp
from src.routes.product import product_bp
from src.routes.sale import sale_bp
from src.routes.expense import expense_bp
from src.routes.savings import savings_bp
from src.routes.voice import voice_bp
from src.routes.dashboard import dashboard_bp
from src.routes.report import report_bp

app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(product_bp, url_prefix="/api/products")
app.register_blueprint(sale_bp, url_prefix="/api/sales")
app.register_blueprint(expense_bp, url_prefix="/api/expenses")
app.register_blueprint(savings_bp, url_prefix="/api/savings")
app.register_blueprint(voice_bp, url_prefix="/api/voice")
app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")
app.register_blueprint(report_bp, url_prefix="/api/reports")

# Route pour servir l\"application React
@app.route("/")
@app.route("/<path:path>")
def serve_react_app(path=""):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, "index.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")


