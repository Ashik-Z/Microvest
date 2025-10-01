# portfolio.py (new file)
from flask import render_template, request, redirect, url_for, session, flash
from utils import buy_stock, get_portfolio, fetch_stock_data
import MySQLdb.cursors

def register_routes(app, mysql):
    @app.route("/portfolio", methods=["GET", "POST"])
    def portfolio():
        if "loggedin" not in session:
            return redirect(url_for('login'))
        
        user_id = session['id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        if request.method == "POST":
            ticker = request.form.get("ticker").upper().strip()
            qty = request.form.get("qty")
            if not ticker or not qty:
                flash("Ticker and quantity are required.", "error")
            else:
                try:
                    qty = int(qty)
                    if qty <= 0:
                        raise ValueError
                except ValueError:
                    flash("Quantity must be a positive integer.", "error")
                    return redirect(url_for('portfolio'))
                
                data = fetch_stock_data(ticker)
                if data:
                    price = float(data['price'])
                    buy_stock(user_id, ticker, qty, price, cursor, mysql.connection)
                    flash(f"Bought {qty} shares of {ticker} at ${price:.2f}.", "success")
                else:
                    flash(f"Ticker {ticker} not found.", "error")
            return redirect(url_for('portfolio'))

        holdings = get_portfolio(user_id, cursor)
        portfolio_data = []
        total_portfolio_value = 0
        total_buy_value = 0
        sp500_data = fetch_stock_data("^GSPC")  # S&P 500 index for market comparison
        
        for holding in holdings:
            data = fetch_stock_data(holding['ticker'])
            if data:
                current_price = float(data['price'])
                buy_price = holding['buy_price']
                qty = holding['qty']
                current_value = current_price * qty
                buy_value = buy_price * qty
                pl = current_value - buy_value
                pl_pct = (pl / buy_value) * 100 if buy_value != 0 else 0
                
                portfolio_data.append({
                    'ticker': holding['ticker'],
                    'qty': qty,
                    'buy_price': f"{buy_price:.2f}",
                    'current_price': f"{current_price:.2f}",
                    'pl': f"{pl:.2f}",
                    'pl_pct': f"{pl_pct:.2f}",
                    'buy_date': holding['buy_date'].strftime("%Y-%m-%d %H:%M:%S")
                })
                total_portfolio_value += current_value
                total_buy_value += buy_value

        total_pl = total_portfolio_value - total_buy_value
        total_pl_pct = (total_pl / total_buy_value) * 100 if total_buy_value != 0 else 0
        
        market_change_pct = float(sp500_data['change_pct']) if sp500_data else 0

        return render_template("portfolio.html", 
                               portfolio_data=portfolio_data,
                               total_portfolio_value=f"{total_portfolio_value:.2f}",
                               total_pl=f"{total_pl:.2f}",
                               total_pl_pct=f"{total_pl_pct:.2f}",
                               market_change_pct=f"{market_change_pct:.2f}")
