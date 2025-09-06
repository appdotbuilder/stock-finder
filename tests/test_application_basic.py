import pytest

from app.database import reset_db
from app.services.stock_service import StockService
from app.services.sector_service import SectorService
from app.services.mock_data_service import MockDataService
from app.models import StockCreate, StockFilter
from decimal import Decimal


@pytest.fixture()
def fresh_db():
    """Provide a fresh database for each test"""
    reset_db()
    yield
    reset_db()


class TestApplicationBasic:
    """Basic tests to ensure the application works"""

    def test_initialize_with_mock_data(self, fresh_db):
        """Test that we can initialize the application with mock data"""
        result = MockDataService.initialize_database()
        assert result is True

        # Should have sectors
        sectors = SectorService.get_all_sectors()
        assert len(sectors) == 10

        # Should have stocks
        stocks = StockService.get_all_stocks()
        assert len(stocks) > 0

    def test_create_and_find_stock(self, fresh_db):
        """Test basic stock operations"""
        # Create sectors first
        sectors = SectorService.create_default_sectors()
        tech_sector = next((s for s in sectors if s.name == "Technology"), None)

        # Create a stock
        stock_data = StockCreate(
            ticker="TEST",
            company_name="Test Corp",
            sector_id=tech_sector.id if tech_sector else None,
            industry="Software",
            pe_ratio=Decimal("15.5"),
            pb_ratio=Decimal("2.1"),
            dividend_yield=Decimal("2.5"),
            market_cap=Decimal("1000000000"),
            current_price=Decimal("50.00"),
        )

        stock = StockService.create_stock(stock_data)
        assert stock.ticker == "TEST"
        assert stock.market_cap_category is not None
        assert stock.market_cap_category.value == "Small Cap"

        # Find the stock
        found = StockService.get_stock_by_ticker("TEST")
        assert found is not None
        assert found.company_name == "Test Corp"

    def test_basic_filtering(self, fresh_db):
        """Test basic stock filtering"""
        # Initialize with sample data
        MockDataService.initialize_database()

        # Test filtering all stocks
        all_stocks, total = StockService.search_and_filter_stocks()
        assert len(all_stocks) > 0
        assert total > 0

        # Test pagination
        first_page, total = StockService.search_and_filter_stocks(limit=5, offset=0)
        assert len(first_page) <= 5

        # Test ticker search
        filters = StockFilter(ticker_search="AAPL")
        apple_stocks, _ = StockService.search_and_filter_stocks(filters)
        if len(apple_stocks) > 0:
            assert all("AAPL" in stock.ticker for stock in apple_stocks)

    def test_undervalued_screening(self, fresh_db):
        """Test undervalued stock screening"""
        # Initialize with sample data
        MockDataService.initialize_database()

        # Run screening
        results = StockService.screen_undervalued_stocks()

        # Should find some undervalued stocks
        assert isinstance(results, list)

        # Check that results have required fields
        if results:
            result = results[0]
            assert hasattr(result, "ticker")
            assert hasattr(result, "overall_score")
            assert hasattr(result, "is_undervalued_pe")
            assert hasattr(result, "is_undervalued_pb")
            assert hasattr(result, "has_high_dividend")

    def test_statistics(self, fresh_db):
        """Test statistics calculation"""
        # Initialize with sample data
        MockDataService.initialize_database()

        stats = StockService.get_stock_statistics()

        assert "total_stocks" in stats
        assert "with_pe_ratio" in stats
        assert "with_pb_ratio" in stats
        assert "with_dividend_yield" in stats

        assert stats["total_stocks"] > 0
        assert stats["with_pe_ratio"] >= 0
        assert stats["with_pb_ratio"] >= 0
        assert stats["with_dividend_yield"] >= 0

    def test_sectors_and_industries(self, fresh_db):
        """Test sector and industry data"""
        # Initialize with sample data
        MockDataService.initialize_database()

        # Test sectors
        sectors = StockService.get_available_sectors()
        assert len(sectors) == 10

        sector_names = [s.name for s in sectors]
        assert "Technology" in sector_names
        assert "Healthcare" in sector_names

        # Test industries
        industries = StockService.get_available_industries()
        assert len(industries) > 0
        assert isinstance(industries[0], str)
