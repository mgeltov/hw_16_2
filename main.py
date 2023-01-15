from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime
from sqlalchemy import Column, Integer, String, or_, desc, func, ForeignKey
from sqlalchemy.orm import relationship
import json

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///:memory:'
app.config['JSON_AS_ASCII'] = False

db = SQLAlchemy(app)

"""
 Создание классов User, Offer, Order (аналог соответствующих таблиц) + функции, формирующие словарь из экземпляра класса
"""
class User(db.Model):
    __tablename__ = 'users'
    id = Column(db.Integer, primary_key=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    age = Column(Integer)
    email = Column(String(200))
    role = Column(String(50))
    phone = Column(String(50))
    def get_user_dict(example):
        return {
            'id': example.id,
            'first_name': example.first_name,
            'last_name': example.last_name,
            'age': example.age,
            'email': example.email,
            'role': example.role,
            'phone': example.phone
        }

class Offer(db.Model):
    __tablename__ = 'offers'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    executor_id = Column(Integer, ForeignKey('users.id'))
    orders = relationship('Order')
    users = relationship("User")
    def get_offer_dict(example):
        return {
            'id': example.id,
            'order_id': example.order_id,
            'executor_id': example.executor_id,
            }

class Order(db.Model):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    name = Column(String(300))
    description = Column(String(300))
    start_date = Column(String(20))
    end_date = Column(String(20))
    address = Column(String(200))
    price = Column(Integer)
    customer_id = Column(Integer, ForeignKey('users.id'))
    executor_id = Column(Integer, ForeignKey('users.id'))
    # users = relationship("User")
    def get_order_dict(example):
        return {
            'id': example.id,
            'name':example.name,
            'description': example.description,
            'start_date': example.start_date,
            'end_date': example.end_date,
            'address': example.address,
            'price': example.price,
            'customer_id': example.customer_id,
            'executor_id': example.executor_id
            }


"""
загрузка данных из файлов json, находящихся в папке data
"""
with open('data/users.json', 'r', encoding='utf-8') as file:
    data = json.load(file)
    users = []
    for user in data:
        user_to_db = User(id=user['id'], first_name=user['first_name'],
                          last_name=user['last_name'], age=user['age'],
                          email=user['email'], role=user['role'],
                          phone=user['phone'])
        users.append(user_to_db)

with open('data/orders.json', 'r', encoding='utf-8') as fp:
    data = json.load(fp)
    orders = []
    for order in data:
        order_to_db = Order(id=order['id'], name=order['name'], description=order['description'],
                            start_date=order['start_date'], end_date=order['end_date'],
                            address=order['address'], price=order['price'],
                            customer_id=order['customer_id'], executor_id=order['executor_id'])
        orders.append(order_to_db)

with open('data/offers.json', 'r') as file:
    data = json.load(file)
    offers = []
    for offer in data:
        offer_to_db = Offer(id=offer['id'], order_id=offer['order_id'],
                            executor_id=offer['executor_id'])
        offers.append(offer_to_db)
"""
создание таблиц БД и заполнение данными из файлов json
"""
with app.app_context():
    db.drop_all()

with app.app_context():
    db.create_all()

    with db.session.begin():
        db.session.add_all(users)
        db.session.add_all(orders)
        db.session.add_all(offers)
        db.session.commit()


"""
Настройка роутов для пользователей
"""
@app.route('/users/', methods=['GET', 'POST'])
def page_users():
    """ Если выбран метод GET, то отражает json; метод POST - добавляет из json"""
    if request.method == 'GET':
        query = db.session.query(User).all()
        users = []
        for user in query:
            users.append(User.get_user_dict(user))
        return jsonify(users)
    elif request.method == 'POST':
        data = request.json
        user_to_load = User(
                            first_name=data.get('first_name'), last_name=data.get('last_name'),
                            age=data.get('age'), email=data.get('email'),
                            role=data.get('role'), phone=data.get('phone')
                            )
        db.session.add(user_to_load)
        db.session.commit()
        return 'Пользователь загружен'

@app.route('/users/<int:uid>', methods=['GET', 'PUT', 'DELETE'])
def page_user_n(uid):
    """ Если выбран метод GET, то отражает json; метод PUT - обновляет из json; метод DELETE - удаляет выбранного пользователя"""
    if request.method == 'GET':
        query = db.session.query(User).filter(User.id == uid).all()
        users = []
        for user in query:
            users.append(User.get_user_dict(user))
        return jsonify(users)
    elif request.method == 'PUT':
        data = request.json
        db.session.query(User).filter(User.id == uid).update(data)
        db.session.commit()
        return 'Пользователь обновлен'
    elif request.method == 'DELETE':
        db.session.query(User).filter(User.id == uid).delete()
        db.session.commit()
        return 'Пользователь удален'



"""
Настройка роутов для заказов
"""
@app.route('/orders/', methods=['GET', 'POST'])
def page_orders():
    """ Если выбран метод GET, то отражает json; метод POST - добавляет из json"""
    if request.method == 'GET':
        query = db.session.query(Order).all()
        orders = []
        for order in query:
            orders.append(Order.get_order_dict(order))
        return jsonify(orders)
    elif request.method == 'POST':
        data = request.json
        order_to_load = Order(
                            name=data.get('name'), description=data.get('description'),
                            start_date=data.get('start_date'), end_date=data.get('end_date'),
                            address=data.get('address'), price=data.get('price'),
                            customer_id=data.get('customer_id'), executor_id=data.get('executor_id')
                            )
        db.session.add(order_to_load)
        db.session.commit()
        return 'Заказ загружен'

@app.route('/orders/<int:oid>', methods=['GET', 'PUT', 'DELETE'])
def page_orders_n(oid):
    """ Если выбран метод GET, то отражает json; метод PUT - обновляет из json; метод DELETE - удаляет выбранного пользователя"""
    if request.method == 'GET':
        query = db.session.query(Order).filter(Order.id == oid).all()
        orders = []
        for order in query:
            orders.append(Order.get_order_dict(order))
        return jsonify(orders)
    elif request.method == 'PUT':
        data = request.json
        db.session.query(Order).filter(Order.id == oid).update(data)
        db.session.commit()
        return 'Заказ обновлен'
    elif request.method == 'DELETE':
        db.session.query(Order).filter(Order.id == oid).delete()
        db.session.commit()
        return 'Заказ удален'

"""
Настройка роутов для предложений
"""
@app.route('/offers/', methods=['GET', 'POST'])
def page_offers():
    """ Если выбран метод GET, то отражает json; метод POST - добавляет из json"""
    if request.method == 'GET':
        query = db.session.query(Offer).all()
        offers = []
        for offer in query:
            offers.append(Offer.get_offer_dict(offer))
        return jsonify(offers)
    elif request.method == 'POST':
        data = request.json
        offer_to_load = Offer(
                            executor_id=data.get('executor_id'), order_id=data.get('order_id'),
                            )
        db.session.add(offer_to_load)
        db.session.commit()
        return 'Заказ загружен'

@app.route('/offers/<int:oid>', methods=['GET', 'PUT', 'DELETE'])
def page_offers_n(oid):
    """ Если выбран метод GET, то отражает json; метод PUT - обновляет из json; метод DELETE - удаляет выбранного пользователя"""
    if request.method == 'GET':
        query = db.session.query(Offer).filter(Offer.id == oid).all()
        offers = []
        for offer in query:
            offers.append(Offer.get_offer_dict(offer))
        return jsonify(offers)
    elif request.method == 'PUT':
        data = request.json
        db.session.query(Offer).filter(Offer.id == oid).update(data)
        db.session.commit()
        return 'Предложение обновлено'
    elif request.method == 'DELETE':
        db.session.query(Offer).filter(Offer.id == oid).delete()
        db.session.commit()
        return 'Предложение удалено'


if __name__ == '__main__':
    app.run()
