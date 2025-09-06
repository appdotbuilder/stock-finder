import pytest

from app.database import reset_db
from app.services.mock_data_service import MockDataService
from app.services.stock_service import StockService
from app.services.sector_service import SectorService


@pytest.fixture()
def fresh_db():
    """Provide a fresh database for each test"""
    reset_db()
    yield
    reset_db()


class TestMockDataService:
    """Test cases for MockDataService"""

    def test_create_mock_stocks_creates_sectors_first(self, fresh_db):
        """Test that creating mock stocks ensures sectors exist"""
        # Verify no sectors initially
        sectors = SectorService.get_all_sectors()
        assert len(sectors) == 0

        # Create mock stocks
        stocks = MockDataService.create_mock_stocks(count=5)

        # Should now have sectors
        sectors = SectorService.get_all_sectors()
        assert len(sectors) == 10  # Default sectors created

        # Should have some stocks
        assert len(stocks) > 0

    def test_create_mock_stocks_realistic_data(self, fresh_db):
        """Test that mock stocks have realistic financial data"""
        stocks = MockDataService.create_mock_stocks(count=10)

        assert len(stocks) >= 5  # Should create several stocks

        # Check some stocks have valid data
        stocks_with_pe = [s for s in stocks if s.pe_ratio is not None]
        stocks_with_pb = [s for s in stocks if s.pb_ratio is not None]
        stocks_with_div = [s for s in stocks if s.dividend_yield is not None]
        stocks_with_mcap = [s for s in stocks if s.market_cap is not None]

        assert len(stocks_with_pe) > 0
        assert len(stocks_with_pb) > 0
        assert len(stocks_with_div) > 0
        assert len(stocks_with_mcap) > 0

        # Verify data is realistic (no negative ratios, etc.)
        for stock in stocks_with_pe:
            assert stock.pe_ratio is not None and stock.pe_ratio >= 0

        for stock in stocks_with_pb:
            assert stock.pb_ratio is not None and stock.pb_ratio >= 0

        for stock in stocks_with_div:
            assert stock.dividend_yield is not None and stock.dividend_yield >= 0
            assert stock.dividend_yield <= 20  # No dividend over 20%

        for stock in stocks_with_mcap:
            assert stock.market_cap is not None and stock.market_cap > 0

    def test_create_mock_stocks_unique_tickers(self, fresh_db):
        """Test that mock stocks have unique tickers"""
        stocks = MockDataService.create_mock_stocks(count=20)

        tickers = [s.ticker for s in stocks]
        unique_tickers = set(tickers)

        assert len(tickers) == len(unique_tickers)  # No duplicates

    def test_create_mock_stocks_no_duplicates_on_repeat(self, fresh_db):
        """Test that creating mock stocks twice doesn't create duplicates"""
        # First creation
        first_stocks = MockDataService.create_mock_stocks(count=10)
        first_count = len(first_stocks)

        # Second creation
        second_stocks = MockDataService.create_mock_stocks(count=10)

        # Should not create duplicates for existing tickers
        assert len(second_stocks) <= first_count

        # Verify total count in database
        all_stocks = StockService.get_all_stocks()
        total_unique_tickers = set(s.ticker for s in all_stocks)
        assert len(all_stocks) == len(total_unique_tickers)

    def test_create_mock_stocks_undervalued_examples(self, fresh_db):
        """Test that mock data includes undervalued stocks for screening"""
        stocks = MockDataService.create_mock_stocks(count=30)

        # Should have some stocks with low P/E ratios
        low_pe_stocks = [s for s in stocks if s.pe_ratio and s.pe_ratio <= 15]
        assert len(low_pe_stocks) > 0

        # Should have some stocks with low P/B ratios
        low_pb_stocks = [s for s in stocks if s.pb_ratio and s.pb_ratio <= 1.5]
        assert len(low_pb_stocks) > 0

        # Should have some stocks with good dividends
        high_div_stocks = [s for s in stocks if s.dividend_yield and s.dividend_yield >= 3.0]
        assert len(high_div_stocks) > 0

    def test_create_mock_stocks_market_cap_categories(self, fresh_db):
        """Test that mock stocks get proper market cap categories"""
        stocks = MockDataService.create_mock_stocks(count=20)

        # Should have stocks in different market cap categories
        categorized_stocks = [s for s in stocks if s.market_cap_category is not None]
        assert len(categorized_stocks) > 0

        # Check that categorization is correct
        for stock in categorized_stocks:
            if stock.market_cap and stock.market_cap_category:
                market_cap_value = float(stock.market_cap)

                if market_cap_value >= 10_000_000_000:  # > $10B
                    assert stock.market_cap_category.value == "Large Cap"
                elif market_cap_value >= 2_000_000_000:  # $2B - $10B
                    assert stock.market_cap_category.value == "Mid Cap"
                elif market_cap_value >= 300_000_000:  # $300M - $2B
                    assert stock.market_cap_category.value == "Small Cap"
                else:  # < $300M
                    assert stock.market_cap_category.value == "Micro Cap"

    def test_create_mock_stocks_sector_assignment(self, fresh_db):
        """Test that mock stocks are assigned to sectors properly"""
        stocks = MockDataService.create_mock_stocks(count=15)

        # Should have stocks assigned to sectors
        stocks_with_sectors = [s for s in stocks if s.sector_id is not None]
        assert len(stocks_with_sectors) > 0

        # Verify sector assignments are valid
        all_sectors = SectorService.get_all_sectors()
        valid_sector_ids = {s.id for s in all_sectors}

        for stock in stocks_with_sectors:
            assert stock.sector_id in valid_sector_ids

    def test_initialize_database_empty(self, fresh_db):
        """Test initializing empty database"""
        result = MockDataService.initialize_database()

        assert result is True

        # Should have sectors
        sectors = SectorService.get_all_sectors()
        assert len(sectors) == 10

        # Should have stocks
        stocks = StockService.get_all_stocks()
        assert len(stocks) >= 10

    def test_initialize_database_already_populated(self, fresh_db):
        """Test initializing database that already has data"""
        # Pre-populate with some data
        SectorService.create_default_sectors()
        MockDataService.create_mock_stocks(count=15)

        initial_stock_count = len(StockService.get_all_stocks())

        # Initialize again
        result = MockDataService.initialize_database()

        assert result is True

        # Should not create many new stocks
        final_stock_count = len(StockService.get_all_stocks())
        assert final_stock_count >= initial_stock_count
        assert final_stock_count < initial_stock_count + 10  # Shouldn't create many new ones

    def test_mock_stocks_have_required_fields(self, fresh_db):
        """Test that all mock stocks have required fields populated"""
        stocks = MockDataService.create_mock_stocks(count=10)

        for stock in stocks:
            # Required fields should always be present
            assert stock.ticker is not None
            assert stock.ticker != ""
            assert stock.company_name is not None
            assert stock.company_name != ""
            assert stock.industry is not None
            assert stock.industry != ""
            assert stock.is_active is True

            # ID should be assigned after creation
            assert stock.id is not None

    def test_financial_ratios_reasonable_ranges(self, fresh_db):
        """Test that financial ratios are in reasonable ranges"""
        stocks = MockDataService.create_mock_stocks(count=25)

        for stock in stocks:
            if stock.pe_ratio is not None:
                assert 0 <= stock.pe_ratio <= 100  # PE ratios typically 0-100

            if stock.pb_ratio is not None:
                assert 0 <= stock.pb_ratio <= 20  # PB ratios typically 0-20

            if stock.dividend_yield is not None:
                assert 0 <= stock.dividend_yield <= 15  # Dividend yields typically 0-15%

            if stock.current_price is not None:
                assert stock.current_price > 0  # Stock prices must be positive
