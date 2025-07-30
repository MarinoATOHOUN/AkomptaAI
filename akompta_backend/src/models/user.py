from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='merchant')  # merchant, admin, operator
    business_name = db.Column(db.String(100))
    business_address = db.Column(db.Text)
    preferred_language = db.Column(db.String(10), default='fr')  # fr, fon, yoruba
    is_active = db.Column(db.Boolean, default=True)
    email_verified = db.Column(db.Boolean, default=False)
    phone_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    products = db.relationship('Product', backref='user', lazy=True, cascade='all, delete-orphan')
    sales = db.relationship('Sale', backref='user', lazy=True, cascade='all, delete-orphan')
    expenses = db.relationship('Expense', backref='user', lazy=True, cascade='all, delete-orphan')
    savings = db.relationship('Savings', backref='user', lazy=True, cascade='all, delete-orphan')
    stock_movements = db.relationship('StockMovement', backref='user', lazy=True, cascade='all, delete-orphan')
    reports = db.relationship('Report', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_total_balance(self):
        """Calcule le solde total (ventes - dépenses + épargne)"""
        total_sales = sum(sale.total_amount for sale in self.sales)
        total_expenses = sum(expense.amount for expense in self.expenses)
        total_savings = sum(saving.amount for saving in self.savings if saving.transaction_type == 'deposit')
        total_withdrawals = sum(saving.amount for saving in self.savings if saving.transaction_type == 'withdrawal')
        
        return total_sales - total_expenses + (total_savings - total_withdrawals)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'phone_number': self.phone_number,
            'role': self.role,
            'business_name': self.business_name,
            'business_address': self.business_address,
            'preferred_language': self.preferred_language,
            'is_active': self.is_active,
            'email_verified': self.email_verified,
            'phone_verified': self.phone_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'total_balance': self.get_total_balance()
        }
    
    def __repr__(self):
        return f'<User {self.username}>'