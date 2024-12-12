import sqlite3
import requests
from bs4 import BeautifulSoup
from time import sleep

# URL и заголовки
url = "https://sb-pizza.ru/"
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}
response = requests.get(url, headers=headers)

# Парсинг данных
soup = BeautifulSoup(response.text, "lxml")
data = soup.find_all("div", class_="dish-card product-card available holder-block rounded")

# Подключение к SQLite
conn = sqlite3.connect("pizzas.db")  # Создаст файл pizzas.db, если он не существует
cursor = conn.cursor()

# Создание таблицы, если она не существует
cursor.execute("""
CREATE TABLE IF NOT EXISTS pizza (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    price REAL,
    weight TEXT,
    ingredients TEXT,
    url_img TEXT
)
""")

for i in data:
    sleep(1)
    name = i.find("h4").text if i.find("h4") else "Не указано"  # Обработка отсутствующего названия
    price_text = i.find("div", class_="price").text.strip() if i.find("div", class_="price") else "0"
    price_text = price_text.replace("₽", "").replace("\xa0", "").replace("От", "").strip()
    try:
        price = float(price_text) if price_text else None  # Преобразование цены в число
    except ValueError:
        price = None

    weight_tag = i.find("div", class_="weight")
    weight = weight_tag.text if weight_tag else None  # Обработка отсутствующего веса

    ingredients_tag = i.find("p")
    ingredients = ingredients_tag.text if ingredients_tag else None  # Обработка отсутствующих ингредиентов

    url_img_tag = i.find("img")
    url_img = url_img_tag.get("src") if url_img_tag else None  # Обработка отсутствующей картинки

    # Вставка данных в базу
    cursor.execute("""
    INSERT INTO pizza (name, price, weight, ingredients, url_img)
    VALUES (?, ?, ?, ?, ?)
    """, (name, price, weight, ingredients, url_img))


conn.commit()
conn.close()


