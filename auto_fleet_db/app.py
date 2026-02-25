from flask import Flask, render_template, request, redirect, url_for, jsonify
from database import db, Vehicle, Mileage, Repair
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///auto_fleet.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Создание таблиц при первом запуске
with app.app_context():
    db.create_all()

# ==================== ВЕБ-ИНТЕРФЕЙС ====================

@app.route('/')
def index():
    """Главная страница"""
    vehicles = Vehicle.query.all()
    total_vehicles = Vehicle.query.count()
    total_repairs = Repair.query.count()
    return render_template('index.html', 
                         vehicles=vehicles,
                         total_vehicles=total_vehicles,
                         total_repairs=total_repairs)

@app.route('/vehicles')
def vehicles():
    """Страница управления автомобилями"""
    all_vehicles = Vehicle.query.order_by(Vehicle.brand).all()
    return render_template('vehicles.html', vehicles=all_vehicles)

@app.route('/vehicles/add', methods=['POST'])
def add_vehicle():
    """Добавление нового автомобиля"""
    brand = request.form['brand']
    model = request.form['model']
    license_plate = request.form['license_plate']
    year = request.form.get('year')
    
    vehicle = Vehicle(
        brand=brand,
        model=model,
        license_plate=license_plate,
        year=year if year else None
    )
    
    db.session.add(vehicle)
    db.session.commit()
    return redirect(url_for('vehicles'))

@app.route('/vehicles/delete/<int:id>')
def delete_vehicle(id):
    """Удаление автомобиля"""
    vehicle = Vehicle.query.get_or_404(id)
    db.session.delete(vehicle)
    db.session.commit()
    return redirect(url_for('vehicles'))

@app.route('/mileage')
def mileage():
    """Страница учета пробега"""
    vehicles = Vehicle.query.all()
    mileage_records = Mileage.query.order_by(Mileage.date.desc()).all()
    return render_template('mileage.html', 
                         vehicles=vehicles, 
                         mileage_records=mileage_records)

@app.route('/mileage/add', methods=['POST'])
def add_mileage():
    """Добавление записи о пробеге"""
    vehicle_id = request.form['vehicle_id']
    date = datetime.strptime(request.form['date'], '%Y-%m-%d')
    mileage_value = request.form['mileage']
    notes = request.form.get('notes', '')
    
    mileage = Mileage(
        vehicle_id=vehicle_id,
        date=date,
        mileage=mileage_value,
        notes=notes
    )
    
    db.session.add(mileage)
    db.session.commit()
    return redirect(url_for('mileage'))

@app.route('/repairs')
def repairs():
    """Страница учета ремонтов"""
    vehicles = Vehicle.query.all()
    repair_records = Repair.query.order_by(Repair.date.desc()).all()
    return render_template('repairs.html', 
                         vehicles=vehicles, 
                         repair_records=repair_records)

@app.route('/repairs/add', methods=['POST'])
def add_repair():
    """Добавление записи о ремонте"""
    vehicle_id = request.form['vehicle_id']
    date = datetime.strptime(request.form['date'], '%Y-%m-%d')
    repair_type = request.form['repair_type']
    description = request.form.get('description', '')
    cost = request.form.get('cost', 0)
    mileage_at_repair = request.form.get('mileage_at_repair', 0)
    
    repair = Repair(
        vehicle_id=vehicle_id,
        date=date,
        repair_type=repair_type,
        description=description,
        cost=float(cost) if cost else None,
        mileage_at_repair=int(mileage_at_repair) if mileage_at_repair else None
    )
    
    db.session.add(repair)
    db.session.commit()
    return redirect(url_for('repairs'))

# ==================== REST API ====================

# API для автомобилей
@app.route('/api/vehicles', methods=['GET'])
def api_get_vehicles():
    vehicles = Vehicle.query.all()
    return jsonify([{
        'id': v.id,
        'brand': v.brand,
        'model': v.model,
        'license_plate': v.license_plate,
        'year': v.year
    } for v in vehicles])

@app.route('/api/vehicles/<int:id>', methods=['GET'])
def api_get_vehicle(id):
    vehicle = Vehicle.query.get_or_404(id)
    return jsonify({
        'id': vehicle.id,
        'brand': vehicle.brand,
        'model': vehicle.model,
        'license_plate': vehicle.license_plate,
        'year': vehicle.year
    })

@app.route('/api/vehicles', methods=['POST'])
def api_create_vehicle():
    data = request.json
    vehicle = Vehicle(
        brand=data['brand'],
        model=data['model'],
        license_plate=data['license_plate'],
        year=data.get('year')
    )
    db.session.add(vehicle)
    db.session.commit()
    return jsonify({'message': 'Автомобиль добавлен', 'id': vehicle.id}), 201

@app.route('/api/vehicles/<int:id>', methods=['PUT'])
def api_update_vehicle(id):
    vehicle = Vehicle.query.get_or_404(id)
    data = request.json
    vehicle.brand = data.get('brand', vehicle.brand)
    vehicle.model = data.get('model', vehicle.model)
    vehicle.license_plate = data.get('license_plate', vehicle.license_plate)
    vehicle.year = data.get('year', vehicle.year)
    db.session.commit()
    return jsonify({'message': 'Автомобиль обновлен'})

@app.route('/api/vehicles/<int:id>', methods=['DELETE'])
def api_delete_vehicle(id):
    vehicle = Vehicle.query.get_or_404(id)
    db.session.delete(vehicle)
    db.session.commit()
    return jsonify({'message': 'Автомобиль удален'})

# API для пробега
@app.route('/api/mileage', methods=['GET'])
def api_get_mileage():
    records = Mileage.query.all()
    return jsonify([{
        'id': m.id,
        'vehicle_id': m.vehicle_id,
        'vehicle_name': str(m.vehicle),
        'date': m.date.strftime('%Y-%m-%d'),
        'mileage': m.mileage,
        'notes': m.notes
    } for m in records])

@app.route('/api/mileage', methods=['POST'])
def api_create_mileage():
    data = request.json
    mileage = Mileage(
        vehicle_id=data['vehicle_id'],
        date=datetime.strptime(data['date'], '%Y-%m-%d'),
        mileage=data['mileage'],
        notes=data.get('notes', '')
    )
    db.session.add(mileage)
    db.session.commit()
    return jsonify({'message': 'Запись пробега добавлена', 'id': mileage.id}), 201

# API для ремонтов
@app.route('/api/repairs', methods=['GET'])
def api_get_repairs():
    records = Repair.query.all()
    return jsonify([{
        'id': r.id,
        'vehicle_id': r.vehicle_id,
        'vehicle_name': str(r.vehicle),
        'date': r.date.strftime('%Y-%m-%d'),
        'repair_type': r.repair_type,
        'description': r.description,
        'cost': r.cost,
        'mileage_at_repair': r.mileage_at_repair
    } for r in records])

@app.route('/api/repairs', methods=['POST'])
def api_create_repair():
    data = request.json
    repair = Repair(
        vehicle_id=data['vehicle_id'],
        date=datetime.strptime(data['date'], '%Y-%m-%d'),
        repair_type=data['repair_type'],
        description=data.get('description', ''),
        cost=data.get('cost'),
        mileage_at_repair=data.get('mileage_at_repair')
    )
    db.session.add(repair)
    db.session.commit()
    return jsonify({'message': 'Запись ремонта добавлена', 'id': repair.id}), 201

if __name__ == '__main__':
    app.run(debug=True, port=5000)
