from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Vehicle(db.Model):
    """Модель для автомобилей"""
    __tablename__ = 'vehicles'
    
    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    license_plate = db.Column(db.String(15), unique=True, nullable=False)
    year = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Связи с другими таблицами
    mileage_records = db.relationship('Mileage', backref='vehicle', lazy=True, cascade='all, delete-orphan')
    repairs = db.relationship('Repair', backref='vehicle', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'{self.brand} {self.model} ({self.license_plate})'

class Mileage(db.Model):
    """Модель для учета пробега"""
    __tablename__ = 'mileage'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    mileage = db.Column(db.Integer, nullable=False)  # Пробег в км
    notes = db.Column(db.Text)
    
    def __repr__(self):
        return f'Пробег {self.mileage} км от {self.date.strftime("%d.%m.%Y")}'

class Repair(db.Model):
    """Модель для учета ремонтов"""
    __tablename__ = 'repairs'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    repair_type = db.Column(db.String(100), nullable=False)  # Тип ремонта
    description = db.Column(db.Text)
    cost = db.Column(db.Float)  # Стоимость ремонта
    mileage_at_repair = db.Column(db.Integer)  # Пробег при ремонте
    
    def __repr__(self):
        return f'Ремонт: {self.repair_type} от {self.date.strftime("%d.%m.%Y")}'