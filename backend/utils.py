import MySQLdb.cursors
import yfinance as yf


# Utility functions for managing the stock watchlist in the database


def add_to_watchlist(user_id, ticker, cursor, db):
    cursor.execute("SELECT * FROM watchlist WHERE user_id = %s AND ticker = %s", (user_id, ticker))
    if cursor.fetchone():
        return False
    cursor.execute("INSERT INTO watchlist (user_id, ticker) VALUES (%s, %s)", (user_id, ticker))
    db.commit()
    return True



def get_watchlist(user_id, cursor):
    cursor.execute("SELECT ticker FROM watchlist WHERE user_id = %s", (user_id,))
    return [row['ticker'] for row in cursor.fetchall()]



def remove_from_watchlist(user_id, ticker, cursor, db):
    cursor.execute("DELETE FROM watchlist WHERE user_id = %s AND ticker = %s", (user_id, ticker))
    db.commit()





# transactions / portfolio management functions


def buy_stock(user_id, ticker, qty, price, cursor, db):
    cursor.execute(
        "INSERT INTO transaction (user_id, ticker, qty, buy_price) VALUES (%s, %s, %s, %s)",
        (user_id, ticker, qty, price)
    )
    db.commit()



def get_portfolio(user_id, cursor):
    cursor.execute(
        "SELECT ticker, qty, buy_price, buy_date FROM transaction WHERE user_id = %s",
        (user_id,)
    )
    return cursor.fetchall()




# fetch stock data using yfinance


def fetch_stock_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period="1d")
        if not data.empty:
            row = data.iloc[-1]
            price = row['Close']
            high = row['High']
            low = row['Low']
            volume = row['Volume']
            prev_close = stock.info.get('previousClose', price)
            change = price - prev_close
            change_pct = (change / prev_close) * 100 if prev_close != 0 else 0
            date_time = row.name.strftime("%Y-%m-%d %H:%M:%S")

            return {
                "ticker": ticker,
                "price": f'{price:.2f}',
                "date_time": date_time,
                "change": f'{change:.2f}',
                "change_pct": f'{change_pct:.2f}',
                "high": f'{high:.2f}',
                "low": f'{low:.2f}',
                "volume": f'{volume:,}'
            }
        else:
            return None
    except Exception:
        return None