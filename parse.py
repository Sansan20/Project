import sqlite3
import requests
from bs4 import BeautifulSoup

url = "https://sb-pizza.ru/"
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}
response = requests.get(url, headers=headers)

soup = BeautifulSoup(response.text, "lxml")
data = soup.find_all("div", class_="dish-card product-card available holder-block rounded")

conn = sqlite3.connect("pizzas.db")
cursor = conn.cursor()

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
    name = i.find("h4").text if i.find("h4") else "Не указано"  # Обработка отсутствующего названия
    price_text = i.find("div", class_="price").text.strip() if i.find("div", class_="price") else "0"
    price_text = price_text.replace("₽", "").replace("\xa0", "").replace("От", "").strip()
    try:
        price = float(price_text) if price_text else None
    except ValueError:
        price = None

    weight_tag = i.find("div", class_="weight")
    weight = weight_tag.text if weight_tag else None

    ingredients_tag = i.find("p")
    ingredients = ingredients_tag.text if ingredients_tag else None

    url_img_tag = i.find("img")
    url_img = url_img_tag.get("src") if url_img_tag else None

    cursor.execute("""
    INSERT INTO pizza (name, price, weight, ingredients, url_img)
    VALUES (?, ?, ?, ?, ?)
    """, (name, price, weight, ingredients, url_img))


conn.commit()
conn.close()