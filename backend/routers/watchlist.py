from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.dependencies import get_current_user
from backend.models import User, Watchlist
from backend.services.stock_service import fetch_multiple, fetch_popular


router = APIRouter(
    tags=["watchlist"]
)
templates = Jinja2Templates(
    directory="backend/templates"
)


@router.get("/watchlist", response_class=HTMLResponse)
async def watchlist_page(
    request     : Request,
    current_user: User = Depends(get_current_user),
    db          : Session = Depends(get_db)
):
    watchlist_entries = (
        db.query(Watchlist)
        .filter(Watchlist.user_id == current_user.id)
        .order_by(Watchlist.added_at.desc())
        .all()
    )
    tickers = [entry.ticker for entry in watchlist_entries]
    stock_data = fetch_multiple(tickers)
    popular_data = fetch_popular()

    return templates.TemplateResponse("watchlist.html", {
        "request": request,
        "user": current_user,
        "stock_data": stock_data,
        "popular_data": popular_data,
        "watchlist_entries": tickers,
    })


@router.post("/watchlist/add", response_class=HTMLResponse)
async def add_ticker(
    ticker: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ticker = ticker.upper().strip()

    existing = (
        db.query(Watchlist)
        .filter(Watchlist.user_id == current_user.id, Watchlist.ticker == ticker)
        .first()
    )

    if not existing:
        from backend.services.stock_service import fetch_stock_data
        data = fetch_stock_data(ticker)
        if data:
            db.add(Watchlist(user_id=current_user.id, ticker=ticker))
            db.commit()

    return RedirectResponse(url="/watchlist", status_code=status.HTTP_302_FOUND)


@router.post("/watchlist/remove", response_class=HTMLResponse)
async def remove_ticker(
    ticker: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ticker = ticker.upper().strip()

    db.query(Watchlist).filter(
        Watchlist.user_id == current_user.id,
        Watchlist.ticker == ticker
    ).delete()
    db.commit()

    return RedirectResponse(url="/watchlist", status_code=status.HTTP_302_FOUND)