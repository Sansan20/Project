from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import requests
from bs4 import BeautifulSoup

# Инициализация базы данных
Base = declarative_base()

class Pizza(Base):
    __tablename__ = 'pizza'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=True)
    weight = Column(String, nullable=True)
    ingredients = Column(String, nullable=True)
    url_img = Column(String, nullable=True)

# Функция для нормализации текста (переводим в верхний регистр)
def normalize_text(text):
    return text.strip().upper() if text else None

# Указываем URL для парсинга
url = "https://sb-pizza.ru/"
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}

# Запрос данных с сайта
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "lxml")

# Ищем все блоки с пиццами
data = soup.find_all("div", class_="dish-card product-card available holder-block rounded")

# Настроим подключение к базе данных
engine = create_engine("sqlite:///pizzas.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Обрабатываем данные и добавляем в базу
for i in data:
    # Получаем название пиццы, приводим к верхнему регистру
    name = normalize_text(i.find("h4").text) if i.find("h4") else "НЕ УКАЗАНО"

    # Получаем цену и обрабатываем её
    price_text = i.find("div", class_="price").text.strip() if i.find("div", class_="price") else "0"
    price_text = price_text.replace("₽", "").replace("\xa0", "").replace("От", "").strip()
    try:
        price = float(price_text) if price_text else None
    except ValueError:
        price = None

    # Получаем вес пиццы, приводим к верхнему регистру
    weight_tag = i.find("div", class_="weight")
    weight = normalize_text(weight_tag.text) if weight_tag else None

    # Получаем ингредиенты, приводим к верхнему регистру
    ingredients_tag = i.find("p")
    ingredients = normalize_text(ingredients_tag.text) if ingredients_tag else None

    # Получаем URL изображения
    url_img_tag = i.find("img")
    url_img = url_img_tag.get("src") if url_img_tag else None

    # Проверяем, существует ли уже такая пицца в базе
    existing_pizza = session.query(Pizza).filter_by(name=name, weight=weight).first()

    # Если пицца существует, обновляем её информацию, иначе добавляем новую
    if existing_pizza:
        existing_pizza.price = price
        existing_pizza.ingredients = ingredients
        existing_pizza.url_img = url_img
    else:
        new_pizza = Pizza(name=name, price=price, weight=weight, ingredients=ingredients, url_img=url_img)
        session.add(new_pizza)

# Сохраняем изменения в базе
session.commit()
session.close()
