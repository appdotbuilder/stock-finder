from app.database import create_tables
import app.stock_screener


def startup() -> None:
    # this function is called before the first request
    create_tables()

    # Initialize stock screener module
    app.stock_screener.create()
