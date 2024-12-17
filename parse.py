from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import requests
from bs4 import BeautifulSoup

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

# Функция для парсинга и добавления данных в базу данных
def parse_and_add_pizzas():
    url = "https://sb-pizza.ru/"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "lxml")
    data = soup.find_all("div", class_="dish-card product-card available holder-block rounded")

    # Процесс парсинга
    for i in data:
        name = i.find("h4").text.strip() if i.find("h4") else "Не указано"  # Обработка отсутствующего названия
        price_text = i.find("div", class_="price").text.strip() if i.find("div", class_="price") else "0"
        price_text = price_text.replace("₽", "").replace("\xa0", "").replace("От", "").strip()
        try:
            price = float(price_text) if price_text else None
        except ValueError:
            price = None

        weight_tag = i.find("div", class_="weight")
        weight = weight_tag.text.strip() if weight_tag else None

        ingredients_tag = i.find("p")
        ingredients = ingredients_tag.text.strip() if ingredients_tag else None

        url_img_tag = i.find("img")
        url_img = url_img_tag.get("src") if url_img_tag else None

        # Проверка существования записи перед добавлением или обновлением
        existing_pizza = Pizza.query.filter_by(name=name, weight=weight).first()

        if existing_pizza:
            existing_pizza.price = price
            existing_pizza.ingredients = ingredients
            existing_pizza.url_img = url_img
        else:
            new_pizza = Pizza(name=name, price=price, weight=weight, ingredients=ingredients, url_img=url_img)
            db.session.add(new_pizza)

    db.session.commit()

# Запуск парсинга и добавления данных в базу
with app.app_context():
    db.create_all()  # Создание таблиц в базе данных (если они еще не существуют)
    parse_and_add_pizzas()
