from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.dependencies import get_current_user
from backend.models import User, Transaction, TransactionType
from backend.services.stock_service import fetch_stock_data, fetch_multiple

router = APIRouter(tags=["portfolio"])
templates = Jinja2Templates(directory="backend/templates")


def get_positions(user_id: int, db: Session) -> list[dict]:
    """
    Aggregates all buy/sell transactions for a user into positions.
    Returns a list of dicts with ticker, qty, avg_cost, current_price, P&L etc.
    """
    transactions = (
        db.query(Transaction)
        .filter(Transaction.user_id == user_id)
        .order_by(Transaction.timestamp.asc())
        .all()
    )
    
    raw: dict = {}

    for t in transactions:
        if t.ticker not in raw:
            raw[t.ticker] = {"qty": 0.0, "total_cost": 0.0}

        if t.type == TransactionType.buy:
            raw[t.ticker]["qty"] += t.qty
            raw[t.ticker]["total_cost"] += t.qty * t.price
        elif t.type == TransactionType.sell:
            if raw[t.ticker]["qty"] > 0:
                avg = raw[t.ticker]["total_cost"] / raw[t.ticker]["qty"]
                raw[t.ticker]["total_cost"] -= avg * t.qty
            raw[t.ticker]["qty"] -= t.qty

    active = {k: v for k, v in raw.items() if v["qty"] > 0.001}

    if not active:
        return []

    live_data = {
        s["ticker"]: s for s in fetch_multiple(list(active.keys()))
    }

    positions = []
    for ticker, pos in active.items():
        avg_cost = pos["total_cost"] / pos["qty"] if pos["qty"] > 0 else 0
        live = live_data.get(ticker)
        current_price = live["price"] if live else avg_cost
        market_value = current_price * pos["qty"]
        pnl = market_value - pos["total_cost"]
        pnl_pct = (pnl / pos["total_cost"]) * 100 if pos["total_cost"] > 0 else 0

        positions.append({
            "ticker": ticker,
            "name": live["name"] if live else ticker,
            "qty": round(pos["qty"], 4),
            "avg_cost": round(avg_cost, 2),
            "current_price": round(current_price, 2),
            "market_value": round(market_value, 2),
            "pnl": round(pnl, 2),
            "pnl_pct": round(pnl_pct, 2),
        })

    return sorted(positions, key=lambda x: x["market_value"], reverse=True)


@router.get("/portfolio", response_class=HTMLResponse)
async def portfolio_page(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    positions = get_positions(current_user.id, db)

    total_value = sum(p["market_value"] for p in positions)
    total_cost = sum(p["avg_cost"] * p["qty"] for p in positions)
    total_pnl = total_value - total_cost
    total_pnl_pct = (total_pnl / total_cost * 100) if total_cost > 0 else 0

    recent_transactions = (
        db.query(Transaction)
        .filter(Transaction.user_id == current_user.id)
        .order_by(Transaction.timestamp.desc())
        .limit(10)
        .all()
    )

    return templates.TemplateResponse("portfolio.html", {
        "request": request,
        "user": current_user,
        "positions": positions,
        "total_value": round(total_value, 2),
        "total_cost": round(total_cost, 2),
        "total_pnl": round(total_pnl, 2),
        "total_pnl_pct": round(total_pnl_pct, 2),
        "recent_transactions": recent_transactions,
    })


@router.post("/portfolio/buy", response_class=HTMLResponse)
async def buy_stock(
    request: Request,
    ticker: str = Form(...),
    qty: float = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ticker = ticker.upper().strip()

    if qty <= 0:
        return RedirectResponse(url="/portfolio", status_code=status.HTTP_302_FOUND)

    data = fetch_stock_data(ticker)
    if not data:
        return RedirectResponse(url="/portfolio", status_code=status.HTTP_302_FOUND)

    transaction = Transaction(
        user_id=current_user.id,
        ticker=ticker,
        qty=qty,
        price=data["price"],
        type=TransactionType.buy,
    )
    db.add(transaction)
    db.commit()

    return RedirectResponse(url="/portfolio", status_code=status.HTTP_302_FOUND)


@router.post("/portfolio/sell", response_class=HTMLResponse)
async def sell_stock(
    request: Request,
    ticker: str = Form(...),
    qty: float = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ticker = ticker.upper().strip()

    if qty <= 0:
        return RedirectResponse(url="/portfolio", status_code=status.HTTP_302_FOUND)


    positions = get_positions(current_user.id, db)
    position = next((p for p in positions if p["ticker"] == ticker), None)

    if not position or position["qty"] < qty:
        return RedirectResponse(url="/portfolio", status_code=status.HTTP_302_FOUND)


    data = fetch_stock_data(ticker)
    if not data:
        return RedirectResponse(url="/portfolio", status_code=status.HTTP_302_FOUND)

    transaction = Transaction(
        user_id=current_user.id,
        ticker=ticker,
        qty=qty,
        price=data["price"],
        type=TransactionType.sell,
    )
    db.add(transaction)
    db.commit()

    return RedirectResponse(url="/portfolio", status_code=status.HTTP_302_FOUND)