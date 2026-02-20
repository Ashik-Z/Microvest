from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from backend.config import settings
from backend.database import Base, engine
from backend import models  # noqa: F401
from backend.routers import auth, dashboard, watchlist, portfolio

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Microvest",
    description="Stock watchlist and portfolio tracker",
    debug=settings.DEBUG,
)

app.mount("/static", StaticFiles(directory="backend/static"), name="static")
templates = Jinja2Templates(directory="backend/templates")

# Routers
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(watchlist.router)
app.include_router(portfolio.router)

# Routers (uncomment as we build them)
# from backend.routers import watchlist, portfolio
# app.include_router(watchlist.router)
# app.include_router(portfolio.router)

@app.get("/")
async def root():
    return RedirectResponse(url="/login")