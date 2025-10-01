# stock_watchlist.py (updated for showcase)
import MySQLdb.cursors
from flask import render_template, request, redirect, url_for, session, flash
from utils import get_watchlist, add_to_watchlist, remove_from_watchlist, fetch_stock_data

POPULAR_TICKERS = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX', 'DIS', 'INTC']  # Preloaded popular stocks

def register_routes(app, mysql):
    @app.route("/index", methods=["GET", "POST"])
    def index():
        if "loggedin" not in session:
            return redirect(url_for('login'))
        
        user_id = session['id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        if request.method == "POST":
            action = request.form.get("action")
            ticker = request.form.get("ticker").upper().strip()
            if action == "add" and ticker:
                data = fetch_stock_data(ticker)
                if data:
                    added = add_to_watchlist(user_id, ticker, cursor, mysql.connection)
                    if added:
                        flash(f"Ticker {ticker} added to watchlist.", "success")
                    else:
                        flash(f"Ticker {ticker} is already in your watchlist.", "error")
                else:
                    flash(f"Ticker {ticker} not found.", "error")
            return redirect(url_for('index'))

        tickers = get_watchlist(user_id, cursor)
        stock_data = [fetch_stock_data(t) for t in tickers if fetch_stock_data(t)]

        # Fetch data for popular tickers showcase
        popular_data = [fetch_stock_data(t) for t in POPULAR_TICKERS if fetch_stock_data(t)]

        return render_template("index.html", stock_data=stock_data, popular_data=popular_data)

    @app.route("/remove/<ticker>")
    def remove(ticker):
        if "loggedin" not in session:
            return redirect(url_for('login'))
        user_id = session['id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        remove_from_watchlist(user_id, ticker, cursor, mysql.connection)
        flash(f"Ticker {ticker} removed from watchlist.", "success")
        return redirect(url_for('index'))