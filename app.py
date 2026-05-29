from flask import Flask, render_template, request, redirect
import sqlite3
import yfinance as yf
from datetime import datetime

app = Flask(__name__)

# ==============================
# DATABASE CONNECTION
# ==============================

conn = sqlite3.connect('database.db', check_same_thread=False)

cursor = conn.cursor()

# ==============================
# CREATE TABLE
# ==============================

cursor.execute('''

CREATE TABLE IF NOT EXISTS portfolio (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    stock_name TEXT,

    quantity INTEGER,

    buy_price REAL

)

''')

conn.commit()

# ==============================
# COMPANY DATA
# ==============================

company_data = {

    "AAPL": {
        "name": "Apple",
        "logo": "/static/icons/aapl.png"
    },

    "TSLA": {
        "name": "Tesla",
        "logo": "/static/icons/tsla.png"
    },

    "GOOGL": {
        "name": "Google",
        "logo": "/static/icons/googl.png"
    },

    "AMZN": {
        "name": "Amazon",
        "logo": "/static/icons/amzn.png"
    },

    "MSFT": {
        "name": "Microsoft",
        "logo": "/static/icons/msft.png"
    },

    "META": {
        "name": "Meta",
        "logo": "/static/icons/meta.png"
    },

    "NFLX": {
        "name": "Netflix",
        "logo": "/static/icons/nflx.png"
    }

}

# ==============================
# HOME PAGE
# ==============================

@app.route('/')

def home():

    return render_template('index.html')

# ==============================
# DASHBOARD
# ==============================

@app.route('/dashboard')

def dashboard():

    # FETCH DATA

    cursor.execute("SELECT * FROM portfolio")

    stocks = cursor.fetchall()

    portfolio_data = []

    total_value = 0

    total_profit = 0

    best_stock = ""

    highest_value = 0

    # PROCESS STOCKS

    for stock in stocks:

        stock_id = stock[0]

        stock_name = stock[1]

        quantity = stock[2]

        buy_price = stock[3]

        # GET LIVE PRICE

        ticker = yf.Ticker(stock_name)

        try:

            current_price = ticker.info['regularMarketPrice']

        except:

            current_price = buy_price

        # TOTAL VALUE

        total = round(current_price * quantity, 2)

        # PROFIT LOSS

        profit_loss = round(

            (current_price - buy_price) * quantity,

            2

        )

        # PERCENTAGE CHANGE

        percentage_change = round(

            ((current_price - buy_price) / buy_price) * 100,

            2

        )

        # TOTAL PORTFOLIO

        total_value += total

        total_profit += profit_loss

        # BEST STOCK

        if total > highest_value:

            highest_value = total

            best_stock = stock_name

        # STORE DATA

        portfolio_data.append({

            'id': stock_id,

            'stock_name': stock_name,

            'company_name': company_data.get(
                stock_name,
                {}
            ).get(
                "name",
                "Unknown"
            ),

            'logo': company_data.get(
                stock_name,
                {}
            ).get(
                "logo",
                "/static/icons/default.png"
            ),

            'quantity': quantity,

            'buy_price': round(buy_price, 2),

            'price': round(current_price, 2),

            'total': total,

            'profit_loss': profit_loss,

            'percentage_change': percentage_change

        })

    # DATE TIME

    current_time = datetime.now().strftime(
        "%d %b %Y %I:%M %p"
    )

    # RENDER PAGE

    return render_template(

        'dashboard.html',

        portfolio=portfolio_data,

        total_value=round(total_value, 2),

        total_profit=round(total_profit, 2),

        best_stock=best_stock,

        total_stocks=len(portfolio_data),

        current_time=current_time

    )

# ==============================
# ADD STOCK
# ==============================

@app.route('/add', methods=['POST'])

def add_stock():

    stock_name = request.form['stock_name'].upper()

    quantity = int(request.form['quantity'])

    buy_price = float(request.form['buy_price'])

    # VALIDATION

    if quantity <= 0 or buy_price <= 0:

        return redirect('/dashboard')

    # INSERT INTO DATABASE

    cursor.execute(

        """

        INSERT INTO portfolio

        (stock_name, quantity, buy_price)

        VALUES (?, ?, ?)

        """,

        (stock_name, quantity, buy_price)

    )

    conn.commit()

    return redirect('/dashboard')

# ==============================
# DELETE STOCK
# ==============================

@app.route('/delete/<int:id>')

def delete_stock(id):

    cursor.execute(

        "DELETE FROM portfolio WHERE id = ?",

        (id,)

    )

    conn.commit()

    return redirect('/dashboard')

# ==============================
# RUN APPLICATION
# ==============================

if __name__ == '__main__':

    app.run(debug=True)