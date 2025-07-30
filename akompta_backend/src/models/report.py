from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class Report(db.Model):
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    report_type = db.Column(db.String(50), nullable=False)  # daily, weekly, monthly, annual
    report_period_start = db.Column(db.DateTime, nullable=False)
    report_period_end = db.Column(db.DateTime, nullable=False)
    total_sales = db.Column(db.Float, default=0)
    total_expenses = db.Column(db.Float, default=0)
    net_profit = db.Column(db.Float, default=0)
    total_savings = db.Column(db.Float, default=0)
    file_path = db.Column(db.String(255))  # Chemin vers le PDF généré
    file_url = db.Column(db.String(255))  # URL publique du rapport
    status = db.Column(db.String(20), default='generated')  # generated, sent, archived
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'report_type': self.report_type,
            'report_period_start': self.report_period_start.isoformat() if self.report_period_start else None,
            'report_period_end': self.report_period_end.isoformat() if self.report_period_end else None,
            'total_sales': self.total_sales,
            'total_expenses': self.total_expenses,
            'net_profit': self.net_profit,
            'total_savings': self.total_savings,
            'file_path': self.file_path,
            'file_url': self.file_url,
            'status': self.status,
            'generated_at': self.generated_at.isoformat() if self.generated_at else None
        }
    
    def __repr__(self):
        return f'<Report {self.id}: {self.report_type} for user {self.user_id}>'

