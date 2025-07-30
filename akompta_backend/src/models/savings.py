from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class Savings(db.Model):
    __tablename__ = 'savings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # deposit, withdrawal
    payment_method = db.Column(db.String(50), default='mobile_money')  # mobile_money, cash, bank
    mobile_money_provider = db.Column(db.String(50))  # mtn_momo, orange_money, moov_money
    transaction_id = db.Column(db.String(100))  # ID de transaction Mobile Money
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'amount': self.amount,
            'transaction_type': self.transaction_type,
            'payment_method': self.payment_method,
            'mobile_money_provider': self.mobile_money_provider,
            'transaction_id': self.transaction_id,
            'transaction_date': self.transaction_date.isoformat() if self.transaction_date else None,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Savings {self.id}: {self.transaction_type} {self.amount} FCFA>'

