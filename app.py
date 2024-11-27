import sqlite3

from flask import Flask, render_template, request, redirect, url_for


app = Flask(__name__, template_folder='templates')
app.secret_key = 'Секретный ключ'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/clients')
def clients():
    search_query = request.args.get('search', '')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM client WHERE company_name LIKE ? ORDER BY -id", ('%' + search_query + '%',))
    data = cursor.fetchall()
    conn.close()

    return render_template('clients.html', clients=data, search_query=search_query)

@app.route('/products')
def products():
    search_query = request.args.get('search', '')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM product WHERE name LIKE ? ORDER BY -id", ('%' + search_query + '%',))
    data = cursor.fetchall()
    conn.close()

    return render_template('products.html', products=data, search_query=search_query)

@app.route('/orders')
def orders():
    search_product = request.args.get('search_product', '')
    search_company = request.args.get('search_company', '')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT orders.id, product.name, client.company_name, orders.quantity, orders.status
        FROM orders
        JOIN product ON orders.product_id = product.id
        JOIN client ON orders.client_id = client.id
        WHERE product.name LIKE ? AND client.company_name LIKE ? ORDER BY -orders.id
    """, ('%' + search_product + '%', '%' + search_company + '%'))
    data = cursor.fetchall()
    conn.close()


    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Получение списка клиентов
    cursor.execute("SELECT * FROM client")
    clients = cursor.fetchall()
    client_names = [client[1] for client in clients]

    # Получение списка товаров
    cursor.execute("SELECT * FROM product")
    products = cursor.fetchall()
    product_names = [product[1] for product in products]

    conn.close()

    return render_template('orders.html', client_names=client_names, product_names=product_names,
        orders=data, search_product=search_product, search_company=search_company)

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        manufacturer = request.form['manufacturer']
        weight = request.form['weight']
        price = request.form['price']
        quantity = request.form['quantity']
        photo_url = request.form['photo_url']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('INSERT INTO product (name, manufacturer, weight, price, quantity, photo_url) VALUES (?, ?, ?, ?, ?, ?)',
                  (name, manufacturer, weight, price, quantity, photo_url))
        conn.commit()
        conn.close()

        return redirect(url_for('products'))

    return render_template('add_product.html')

@app.route('/add_company', methods=['GET', 'POST'])
def add_company():
    if request.method == 'POST':
        company_name = request.form['company_name']
        address = request.form['address']
        contact_number = request.form['contact_number']
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO client (company_name, address, contact_number) VALUES (?, ?, ?)", (company_name, address, contact_number))
        conn.commit()
        conn.close()
        return redirect(url_for('clients'))
    return render_template('add_company.html')

@app.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM product WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('products'))

@app.route('/delete_client/<int:company_id>', methods=['POST'])
def delete_client(company_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM client WHERE id = ?", (company_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('clients'))

@app.route('/delete_order/<int:order_id>', methods=['POST'])
def delete_order(order_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM orders WHERE id = ?", (order_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('orders'))

@app.route('/cart', methods=['GET', 'POST'])
def cart():
    if request.method == 'POST':
        # Получаем данные из формы
        client = request.form['client']
        products = request.form.getlist('product')
        quantities = request.form.getlist('quantity')

        # Устанавливаем соединение с базой данных
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        try:
            products_list = []

            # Получаем идентификатор клиента
            cursor.execute("SELECT id FROM client WHERE company_name = ?", (client,))
            client_id = cursor.fetchone()[0]

            # Вставляем заказ в таблицу orders
            for i in range(len(products)):
                product = products[i]
                quantity = int(quantities[i])

                # Получаем идентификатор товара
                cursor.execute("SELECT id, name, price FROM product WHERE name = ?", (product,))
                product_id, product_name, product_price = cursor.fetchone()
                products_list.append([product_name, str(product_price), str(quantity)])

                # Вставляем заказ в таблицу orders
                cursor.execute("INSERT INTO orders (product_id, client_id, quantity) VALUES (?, ?, ?)",
                               (product_id, client_id, quantity))

            # Сохраняем изменения в базе данных
            conn.commit()
        finally:
            # Закрываем соединение с базой данных
            conn.close()

        return redirect(url_for('orders'))

    else:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Получение списка клиентов
        cursor.execute("SELECT * FROM client")
        clients = cursor.fetchall()
        client_names = [client[1] for client in clients]

        # Получение списка товаров
        cursor.execute("SELECT * FROM product")
        products = cursor.fetchall()
        product_names = [product[1] for product in products]

        conn.close()

        product_prices = {}
        for row in products:
            product_name, price = row[1], row[4]
            product_prices[product_name] = price

        return render_template('cart.html', client_names=client_names, product_names=product_names,
            product_prices=str(product_prices))


# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True)
