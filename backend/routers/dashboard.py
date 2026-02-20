from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.dependencies import get_current_user
from backend.models import User, Watchlist, Transaction
from backend.routers.portfolio import get_positions
from backend.services.stock_service import fetch_multiple


router = APIRouter(
    tags=["dashboard"]
)
templates = Jinja2Templates(
    directory="backend/templates"
)


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request         : Request,
    current_user    : User = Depends(get_current_user),
    db              : Session = Depends(get_db)
):
    positions = get_positions(current_user.id, db)
    total_value = round(sum(p["market_value"] for p in positions), 2)
    total_cost = round(sum(p["avg_cost"] * p["qty"] for p in positions), 2)
    total_pnl = round(total_value - total_cost, 2)
    total_pnl_pct = round((total_pnl / total_cost * 100) if total_cost > 0 else 0, 2)

    watchlist_entries = (
        db.query(Watchlist)
        .filter(Watchlist.user_id == current_user.id)
        .all()
    )
    tickers = [e.ticker for e in watchlist_entries]
    watchlist_data = fetch_multiple(tickers)

    recent_transactions = (
        db.query(Transaction)
        .filter(Transaction.user_id == current_user.id)
        .order_by(Transaction.timestamp.desc())
        .limit(5)
        .all()
    )

    return templates.TemplateResponse("dashboard.html", {
        "request"               : request,
        "user"                  : current_user,
        "total_value"           : total_value,
        "total_cost"            : total_cost,
        "total_pnl"             : total_pnl,
        "total_pnl_pct"         : total_pnl_pct,
        "positions"             : positions,
        "watchlist_data"        : watchlist_data,
        "recent_transactions"   : recent_transactions,
        "watchlist_count"       : len(tickers),
    })