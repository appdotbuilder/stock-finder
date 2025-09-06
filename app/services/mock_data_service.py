from typing import List
from decimal import Decimal
import random
import logging

from app.models import Stock, StockCreate
from app.services.stock_service import StockService
from app.services.sector_service import SectorService

logger = logging.getLogger(__name__)


class MockDataService:
    """Service for generating mock stock data"""

    @staticmethod
    def create_mock_stocks(count: int = 50) -> List[Stock]:
        """Create mock stocks with realistic financial data"""

        # Ensure sectors exist first
        sectors = SectorService.get_all_sectors()
        if not sectors:
            sectors = SectorService.create_default_sectors()

        # Mock company data with realistic financial metrics
        mock_companies = [
            # Technology
            {
                "ticker": "AAPL",
                "name": "Apple Inc.",
                "sector": "Technology",
                "industry": "Consumer Electronics",
                "pe": 28.5,
                "pb": 8.2,
                "div": 0.5,
                "mcap": 2800000000000,
                "price": 185.50,
            },
            {
                "ticker": "MSFT",
                "name": "Microsoft Corporation",
                "sector": "Technology",
                "industry": "Software",
                "pe": 32.1,
                "pb": 12.4,
                "div": 0.68,
                "mcap": 2600000000000,
                "price": 350.25,
            },
            {
                "ticker": "GOOGL",
                "name": "Alphabet Inc.",
                "sector": "Technology",
                "industry": "Internet Services",
                "pe": 26.8,
                "pb": 5.1,
                "div": 0.0,
                "mcap": 1650000000000,
                "price": 135.75,
            },
            {
                "ticker": "NVDA",
                "name": "NVIDIA Corporation",
                "sector": "Technology",
                "industry": "Semiconductors",
                "pe": 45.2,
                "pb": 13.7,
                "div": 0.16,
                "mcap": 1400000000000,
                "price": 465.80,
            },
            {
                "ticker": "META",
                "name": "Meta Platforms Inc.",
                "sector": "Technology",
                "industry": "Social Media",
                "pe": 22.4,
                "pb": 4.8,
                "div": 0.0,
                "mcap": 750000000000,
                "price": 295.15,
            },
            # Healthcare
            {
                "ticker": "JNJ",
                "name": "Johnson & Johnson",
                "sector": "Healthcare",
                "industry": "Pharmaceuticals",
                "pe": 15.8,
                "pb": 4.2,
                "div": 2.95,
                "mcap": 420000000000,
                "price": 162.40,
            },
            {
                "ticker": "UNH",
                "name": "UnitedHealth Group",
                "sector": "Healthcare",
                "industry": "Health Insurance",
                "pe": 24.3,
                "pb": 5.8,
                "div": 1.88,
                "mcap": 480000000000,
                "price": 520.75,
            },
            {
                "ticker": "PFE",
                "name": "Pfizer Inc.",
                "sector": "Healthcare",
                "industry": "Pharmaceuticals",
                "pe": 12.1,
                "pb": 2.1,
                "div": 3.44,
                "mcap": 210000000000,
                "price": 37.25,
            },
            # Financials - Many undervalued
            {
                "ticker": "JPM",
                "name": "JPMorgan Chase & Co.",
                "sector": "Financials",
                "industry": "Banking",
                "pe": 11.2,
                "pb": 1.6,
                "div": 3.0,
                "mcap": 440000000000,
                "price": 150.80,
            },
            {
                "ticker": "BAC",
                "name": "Bank of America Corp",
                "sector": "Financials",
                "industry": "Banking",
                "pe": 9.8,
                "pb": 1.1,
                "div": 2.4,
                "mcap": 280000000000,
                "price": 34.90,
            },
            {
                "ticker": "WFC",
                "name": "Wells Fargo & Company",
                "sector": "Financials",
                "industry": "Banking",
                "pe": 10.5,
                "pb": 0.9,
                "div": 2.8,
                "mcap": 170000000000,
                "price": 42.15,
            },
            {
                "ticker": "GS",
                "name": "Goldman Sachs Group",
                "sector": "Financials",
                "industry": "Investment Banking",
                "pe": 8.4,
                "pb": 1.2,
                "div": 2.5,
                "mcap": 120000000000,
                "price": 350.60,
            },
            # Energy - Undervalued sector
            {
                "ticker": "XOM",
                "name": "Exxon Mobil Corporation",
                "sector": "Energy",
                "industry": "Oil & Gas",
                "pe": 12.8,
                "pb": 1.8,
                "div": 5.8,
                "mcap": 420000000000,
                "price": 105.40,
            },
            {
                "ticker": "CVX",
                "name": "Chevron Corporation",
                "sector": "Energy",
                "industry": "Oil & Gas",
                "pe": 13.5,
                "pb": 1.5,
                "div": 3.4,
                "mcap": 300000000000,
                "price": 158.90,
            },
            {
                "ticker": "COP",
                "name": "ConocoPhillips",
                "sector": "Energy",
                "industry": "Oil & Gas",
                "pe": 11.2,
                "pb": 1.7,
                "div": 2.1,
                "mcap": 150000000000,
                "price": 118.75,
            },
            # Utilities - High dividend
            {
                "ticker": "NEE",
                "name": "NextEra Energy Inc.",
                "sector": "Utilities",
                "industry": "Electric Utilities",
                "pe": 22.4,
                "pb": 2.8,
                "div": 3.2,
                "mcap": 150000000000,
                "price": 75.30,
            },
            {
                "ticker": "DUK",
                "name": "Duke Energy Corporation",
                "sector": "Utilities",
                "industry": "Electric Utilities",
                "pe": 19.6,
                "pb": 1.4,
                "div": 4.1,
                "mcap": 75000000000,
                "price": 98.25,
            },
            {
                "ticker": "SO",
                "name": "Southern Company",
                "sector": "Utilities",
                "industry": "Electric Utilities",
                "pe": 21.8,
                "pb": 1.6,
                "div": 3.9,
                "mcap": 74000000000,
                "price": 69.85,
            },
            # Consumer Staples
            {
                "ticker": "PG",
                "name": "Procter & Gamble Co",
                "sector": "Consumer Staples",
                "industry": "Household Products",
                "pe": 24.2,
                "pb": 7.8,
                "div": 2.4,
                "mcap": 360000000000,
                "price": 152.70,
            },
            {
                "ticker": "KO",
                "name": "The Coca-Cola Company",
                "sector": "Consumer Staples",
                "industry": "Beverages",
                "pe": 26.4,
                "pb": 9.2,
                "div": 3.1,
                "mcap": 260000000000,
                "price": 59.85,
            },
            {
                "ticker": "WMT",
                "name": "Walmart Inc.",
                "sector": "Consumer Staples",
                "industry": "Retail",
                "pe": 27.1,
                "pb": 5.1,
                "div": 1.8,
                "mcap": 420000000000,
                "price": 158.40,
            },
            # Real Estate - High dividend
            {
                "ticker": "AMT",
                "name": "American Tower Corp",
                "sector": "Real Estate",
                "industry": "REITs",
                "pe": 45.2,
                "pb": 6.8,
                "div": 3.1,
                "mcap": 95000000000,
                "price": 207.90,
            },
            {
                "ticker": "PLD",
                "name": "Prologis Inc.",
                "sector": "Real Estate",
                "industry": "REITs",
                "pe": 38.4,
                "pb": 2.4,
                "div": 2.8,
                "mcap": 110000000000,
                "price": 118.65,
            },
            {
                "ticker": "SPG",
                "name": "Simon Property Group",
                "sector": "Real Estate",
                "industry": "REITs",
                "pe": 16.8,
                "pb": 1.5,
                "div": 6.2,
                "mcap": 42000000000,
                "price": 128.75,
            },
        ]

        # Add more diverse stocks for better screening
        additional_stocks = []
        sector_names = [s.name for s in sectors]

        # Generate additional undervalued stocks
        undervalued_tickers = [
            "INTC",
            "T",
            "VZ",
            "IBM",
            "F",
            "GM",
            "C",
            "USB",
            "PNC",
            "TFC",
            "KEY",
            "RF",
            "ZION",
            "BBY",
            "KSS",
            "M",
            "JCP",
            "GPS",
            "ANF",
            "AEO",
            "EXPR",
            "TLRY",
            "CGC",
            "ACB",
            "HEXO",
            "OGI",
            "CRON",
        ]

        for i, ticker in enumerate(undervalued_tickers):
            sector = random.choice(sector_names)
            pe_ratio = round(random.uniform(5.0, 15.0), 1)  # Low PE
            pb_ratio = round(random.uniform(0.5, 1.4), 1)  # Low PB
            div_yield = round(random.uniform(2.0, 6.0), 1)  # Good dividend
            market_cap = random.randint(1000000000, 50000000000)  # $1B - $50B
            price = round(random.uniform(15.0, 150.0), 2)

            additional_stocks.append(
                {
                    "ticker": ticker,
                    "name": f"Undervalued Corp {i + 1}",
                    "sector": sector,
                    "industry": f"{sector} Services",
                    "pe": pe_ratio,
                    "pb": pb_ratio,
                    "div": div_yield,
                    "mcap": market_cap,
                    "price": price,
                }
            )

        # Combine all stocks
        all_stocks = mock_companies + additional_stocks[: count - len(mock_companies)]

        # Create sector lookup
        sector_lookup = {s.name: s.id for s in sectors}

        created_stocks = []
        for stock_data in all_stocks[:count]:
            try:
                # Check if stock already exists
                existing = StockService.get_stock_by_ticker(stock_data["ticker"])
                if existing:
                    continue

                stock_create = StockCreate(
                    ticker=stock_data["ticker"],
                    company_name=stock_data["name"],
                    sector_id=sector_lookup.get(stock_data["sector"]),
                    industry=stock_data["industry"],
                    pe_ratio=Decimal(str(stock_data["pe"])) if stock_data.get("pe") else None,
                    pb_ratio=Decimal(str(stock_data["pb"])) if stock_data.get("pb") else None,
                    dividend_yield=Decimal(str(stock_data["div"])) if stock_data.get("div") else None,
                    market_cap=Decimal(str(stock_data["mcap"])) if stock_data.get("mcap") else None,
                    current_price=Decimal(str(stock_data["price"])) if stock_data.get("price") else None,
                )

                stock = StockService.create_stock(stock_create)
                created_stocks.append(stock)

            except Exception as e:
                logger.warning(f"Error creating stock {stock_data['ticker']}: {e}")
                continue

        return created_stocks

    @staticmethod
    def initialize_database():
        """Initialize database with sectors and mock stocks"""
        # Create sectors first
        sectors = SectorService.get_all_sectors()
        if not sectors:
            sectors = SectorService.create_default_sectors()
            logger.info(f"Created {len(sectors)} sectors")

        # Create mock stocks
        existing_stocks = StockService.get_all_stocks()
        if len(existing_stocks) < 10:  # Create stocks if we don't have many
            new_stocks = MockDataService.create_mock_stocks(50)
            logger.info(f"Created {len(new_stocks)} mock stocks")
        else:
            logger.info(f"Database already has {len(existing_stocks)} stocks")

        return True
