from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class Expense(db.Model):
    __tablename__ = 'expenses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100))  # transport, achat_stock, equipement, etc.
    expense_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_method = db.Column(db.String(50), default='cash')
    receipt_url = db.Column(db.String(255))  # URL vers le reçu scanné
    notes = db.Column(db.Text)
    voice_command = db.Column(db.Text)  # Commande vocale originale
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'description': self.description,
            'amount': self.amount,
            'category': self.category,
            'expense_date': self.expense_date.isoformat() if self.expense_date else None,
            'payment_method': self.payment_method,
            'receipt_url': self.receipt_url,
            'notes': self.notes,
            'voice_command': self.voice_command,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Expense {self.id}: {self.description} - {self.amount} FCFA>'

