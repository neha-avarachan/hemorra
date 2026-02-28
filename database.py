from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    college_id = db.Column(db.String(50), unique=True, nullable=False)
    blood_group = db.Column(db.String(5), nullable=False)
    weight = db.Column(db.Float, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    last_donation_date = db.Column(db.DateTime, nullable=True)
    is_available = db.Column(db.Boolean, default=True)
    next_eligible_date = db.Column(db.DateTime, nullable=True)
    donate_count = db.Column(db.Integer, default=0)
    password = db.Column(db.String(200), nullable=False)
    telegram_chat_id = db.Column(db.String(100), nullable=True)

class BloodRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    requester_name = db.Column(db.String(100), nullable=False)
    requester_phone = db.Column(db.String(20), nullable=False)
    blood_group = db.Column(db.String(5), nullable=False)
    hospital = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    urgency = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='active')
    unique_code = db.Column(db.String(10), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class DonorResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('blood_request.id'), nullable=False)
    donor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='notified')
    # status options: notified, seen, confirmed, donated, declined
    created_at = db.Column(db.DateTime, default=datetime.utcnow)