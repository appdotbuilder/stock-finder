import pytest
from decimal import Decimal

from app.database import reset_db
from app.services.stock_service import StockService
from app.services.sector_service import SectorService
from app.models import StockCreate, StockFilter


@pytest.fixture()
def fresh_db():
    """Provide a fresh database for each test"""
    reset_db()
    yield
    reset_db()


@pytest.fixture()
def basic_data(fresh_db):
    """Create basic test data"""
    # Create sectors
    sectors = SectorService.create_default_sectors()
    tech_sector = next((s for s in sectors if s.name == "Technology"), None)

    # Create a few test stocks
    stocks_data = [
        StockCreate(
            ticker="AAPL",
            company_name="Apple Inc.",
            sector_id=tech_sector.id if tech_sector else None,
            industry="Consumer Electronics",
            pe_ratio=Decimal("28.5"),
            pb_ratio=Decimal("8.2"),
            dividend_yield=Decimal("0.5"),
            market_cap=Decimal("2800000000000"),
            current_price=Decimal("185.50"),
        ),
        StockCreate(
            ticker="UNDERVAL",
            company_name="Undervalued Corp",
            sector_id=tech_sector.id if tech_sector else None,
            industry="Banking",
            pe_ratio=Decimal("8.5"),
            pb_ratio=Decimal("1.2"),
            dividend_yield=Decimal("4.5"),
            market_cap=Decimal("50000000000"),
            current_price=Decimal("45.30"),
        ),
    ]

    created_stocks = []
    for stock_data in stocks_data:
        stock = StockService.create_stock(stock_data)
        created_stocks.append(stock)

    return created_stocks


class TestStockServiceCore:
    """Core tests for StockService functionality"""

    def test_create_and_retrieve_stock(self, basic_data):
        """Test basic stock creation and retrieval"""
        stocks = StockService.get_all_stocks()
        assert len(stocks) == 2

        apple = StockService.get_stock_by_ticker("AAPL")
        assert apple is not None
        assert apple.company_name == "Apple Inc."
        assert apple.pe_ratio == Decimal("28.5")

    def test_filter_by_ticker(self, basic_data):
        """Test filtering stocks by ticker"""
        filters = StockFilter(ticker_search="AAPL")
        stocks, total = StockService.search_and_filter_stocks(filters)

        assert len(stocks) == 1
        assert stocks[0].ticker == "AAPL"

    def test_filter_by_pe_ratio(self, basic_data):
        """Test filtering by P/E ratio"""
        filters = StockFilter(max_pe_ratio=Decimal("15"))
        stocks, total = StockService.search_and_filter_stocks(filters)

        assert len(stocks) == 1
        assert stocks[0].ticker == "UNDERVAL"

    def test_screen_undervalued(self, basic_data):
        """Test undervalued stock screening"""
        results = StockService.screen_undervalued_stocks()

        # Should find UNDERVAL as it meets criteria
        assert len(results) >= 1
        underval_result = next((r for r in results if r.ticker == "UNDERVAL"), None)
        assert underval_result is not None

    def test_get_statistics(self, basic_data):
        """Test statistics calculation"""
        stats = StockService.get_stock_statistics()

        assert stats["total_stocks"] == 2
        assert stats["with_pe_ratio"] == 2
        assert stats["with_pb_ratio"] == 2
