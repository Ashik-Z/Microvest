# Microvest

A stock watchlist and portfolio tracker built with FastAPI, SQLAlchemy, MySQL, and Tailwind CSS.

---

## Features

- User registration and login with secure session cookies and bcrypt password hashing
- Watchlist to track stock tickers with live prices
- Portfolio to buy and sell stocks at live market prices with P&L tracking
- Dashboard overview of portfolio value, P&L, watchlist and recent transactions
- Live stock data powered by yfinance with 60-second caching

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python) |
| Database | MySQL + SQLAlchemy 2.0 |
| Auth | itsdangerous + passlib/bcrypt |
| Stock Data | yfinance |
| Templates | Jinja2 + Tailwind CSS + Alpine.js |

---

## Project Structure

```
Microvest/
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── dependencies.py
│   ├── routers/
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── watchlist.py
│   │   └── portfolio.py
│   ├── services/
│   │   ├── auth_service.py
│   │   └── stock_service.py
│   └── templates/
│       ├── base.html
│       ├── login.html
│       ├── register.html
│       ├── dashboard.html
│       ├── watchlist.html
│       └── portfolio.html
├── .env
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Clone and create virtual environment

```bash
git clone https://github.com/Ashik-Z/Microvest.git
cd Microvest
python -m venv venv
venv\scripts\activate.ps1  # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the root:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=microvest
SECRET_KEY=your-secret-key-here
DEBUG=True
```

Generate a secret key:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 4. Set up the database

- Start your MySQL server (XAMPP, standalone MySQL, or any MySQL-compatible server)
- Create a database named `microvest`
- Tables are created automatically on first run

### 5. Run the app

```bash
uvicorn backend.main:app --reload
```

Visit `http://127.0.0.1:8000`

---

## License

MIT
