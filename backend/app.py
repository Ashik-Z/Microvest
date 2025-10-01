# app.py (updated)
from flask import Flask
from flask_mysqldb import MySQL
from stock_watchlist import register_routes as register_watchlist_routes
from login_register import register_routes as register_auth_routes
from portfolio import register_routes as register_portfolio_routes  # New import

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'be5f1f442394779ce1bf2162b062e637'

# MySQL Config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '123456'
app.config['MYSQL_DB'] = 'microvest'

mysql = MySQL(app)

# Register routes from stock_watchlist, login_register, and portfolio
register_watchlist_routes(app, mysql)
register_auth_routes(app, mysql)
register_portfolio_routes(app, mysql)  # Register new portfolio routes

if __name__ == "__main__":
    app.run(debug=True)