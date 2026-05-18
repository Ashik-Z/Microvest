from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.dependencies import get_current_user
from backend.models import User, Watchlist
from backend.routers.portfolio import get_positions
from backend.services.stock_service import fetch_multiple
from backend.services.inflation_service import (
    fetch_exchange_rates,
    fetch_inflation_rates,
    fetch_commodity_prices,
    calculate_real_returns,
)

router = APIRouter(tags=["inflation"])
templates = Jinja2Templates(directory="backend/templates")

DEFAULT_INFLATION_RATE = 3.5


@router.get("/inflation", response_class=HTMLResponse)
async def inflation_dashboard(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    exchange_rates = fetch_exchange_rates()
    inflation_rates = fetch_inflation_rates()
    commodities = fetch_commodity_prices()

    us_inflation = DEFAULT_INFLATION_RATE
    for entry in inflation_rates:
        if entry["code"] == "US":
            us_inflation = entry["rate"]
            break

    watchlist_entries = (
        db.query(Watchlist)
        .filter(Watchlist.user_id == current_user.id)
        .all()
    )
    watchlist_tickers = [e.ticker for e in watchlist_entries]
    watchlist_stocks = fetch_multiple(watchlist_tickers)

    watchlist_real_returns = calculate_real_returns(
        watchlist_stocks, us_inflation / 252  
    ) if watchlist_stocks else []

    positions = get_positions(current_user.id, db)

    portfolio_real_returns = calculate_real_returns(
        positions, us_inflation
    ) if positions else []

    return templates.TemplateResponse("inflation.html", {
        "request": request,
        "user": current_user,
        "exchange_rates": exchange_rates,
        "inflation_rates": inflation_rates,
        "commodities": commodities,
        "us_inflation": us_inflation,
        "watchlist_real_returns": watchlist_real_returns,
        "portfolio_real_returns": portfolio_real_returns,
    })