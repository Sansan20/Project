from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

# Инициализация Flask-приложения и SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pizzas.db'  # Путь к базе данных
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Отключение отслеживания изменений
db = SQLAlchemy(app)

# Определение модели для таблицы pizza
class Pizza(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, nullable=True)
    weight = db.Column(db.String, nullable=True)
    ingredients = db.Column(db.String, nullable=True)
    url_img = db.Column(db.String, nullable=True)

# Функция для получения отфильтрованных пицц
def get_filtered_pizzas(order_by="price", order_dir="asc", price_min=None, price_max=None):
    query = Pizza.query
    if price_min is not None:
        query = query.filter(Pizza.price >= price_min)
    if price_max is not None:
        query = query.filter(Pizza.price <= price_max)

    # Сортировка
    if order_dir == "asc":
        query = query.order_by(getattr(Pizza, order_by).asc())
    else:
        query = query.order_by(getattr(Pizza, order_by).desc())

    return query.all()

# Главная страница с фильтрацией пицц
@app.route('/')
def index():
    order_by = request.args.get("order_by", "price")
    order_dir = request.args.get("order_dir", "asc")
    price_min = request.args.get("price_min")
    price_max = request.args.get("price_max")

    try:
        price_min = float(price_min) if price_min else None
        price_max = float(price_max) if price_max else None
    except ValueError:
        price_min = price_max = None

    pizzas = get_filtered_pizzas(order_by, order_dir, price_min, price_max)
    return render_template("index.html", pizzas=pizzas, order_by=order_by, order_dir=order_dir, price_min=price_min, price_max=price_max)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)