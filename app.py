from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

def get_filtered_pizzas(order_by="price", order_dir="asc", price_min=None, price_max=None):
    """Получает данные из базы данных с фильтрацией."""
    conn = sqlite3.connect("pizzas.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = "SELECT * FROM pizza WHERE 1=1"
    params = []

    # Фильтр по цене
    if price_min is not None:
        query += " AND price >= ?"
        params.append(price_min)
    if price_max is not None:
        query += " AND price <= ?"
        params.append(price_max)

    # Добавление сортировки
    query += f" ORDER BY {order_by} {order_dir.upper()}"

    cursor.execute(query, params)
    pizzas = cursor.fetchall()
    conn.close()
    return pizzas

@app.route('/')
def index():
    # Получение параметров из запроса
    order_by = request.args.get("order_by", "price")
    order_dir = request.args.get("order_dir", "asc")
    price_min = request.args.get("price_min")
    price_max = request.args.get("price_max")

    # Приведение диапазона цен к числам, если они заданы
    try:
        price_min = float(price_min) if price_min else None
        price_max = float(price_max) if price_max else None
    except ValueError:
        price_min = price_max = None

    # Получение данных из базы
    pizzas = get_filtered_pizzas(order_by, order_dir, price_min, price_max)
    return render_template("index.html", pizzas=pizzas, order_by=order_by, order_dir=order_dir, price_min=price_min, price_max=price_max)

if __name__ == "__main__":
    app.run(debug=True)
