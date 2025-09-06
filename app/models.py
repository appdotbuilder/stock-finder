from sqlmodel import SQLModel, Field, Relationship, JSON, Column
from datetime import datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal
from enum import Enum


class SectorEnum(str, Enum):
    """Enumeration of stock market sectors"""

    TECHNOLOGY = "Technology"
    HEALTHCARE = "Healthcare"
    FINANCIALS = "Financials"
    CONSUMER_DISCRETIONARY = "Consumer Discretionary"
    CONSUMER_STAPLES = "Consumer Staples"
    INDUSTRIALS = "Industrials"
    ENERGY = "Energy"
    MATERIALS = "Materials"
    UTILITIES = "Utilities"
    REAL_ESTATE = "Real Estate"
    TELECOMMUNICATIONS = "Telecommunications"


class MarketCapEnum(str, Enum):
    """Enumeration of market cap categories"""

    LARGE_CAP = "Large Cap"  # > $10B
    MID_CAP = "Mid Cap"  # $2B - $10B
    SMALL_CAP = "Small Cap"  # $300M - $2B
    MICRO_CAP = "Micro Cap"  # < $300M


# Persistent models (stored in database)
class Sector(SQLModel, table=True):
    """Sector reference data with industry averages"""

    __tablename__ = "sectors"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, unique=True)
    description: str = Field(default="", max_length=500)
    average_pe_ratio: Optional[Decimal] = Field(default=None, decimal_places=2)
    average_pb_ratio: Optional[Decimal] = Field(default=None, decimal_places=2)
    average_dividend_yield: Optional[Decimal] = Field(default=None, decimal_places=2)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    stocks: List["Stock"] = Relationship(back_populates="sector")


class Stock(SQLModel, table=True):
    """Main stock model with financial metrics"""

    __tablename__ = "stocks"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    ticker: str = Field(max_length=10, unique=True, index=True)
    company_name: str = Field(max_length=200)
    sector_id: Optional[int] = Field(default=None, foreign_key="sectors.id")
    industry: str = Field(max_length=100)

    # Financial metrics
    pe_ratio: Optional[Decimal] = Field(default=None, decimal_places=2, description="Price-to-Earnings ratio")
    pb_ratio: Optional[Decimal] = Field(default=None, decimal_places=2, description="Price-to-Book ratio")
    dividend_yield: Optional[Decimal] = Field(default=None, decimal_places=2, description="Dividend yield percentage")
    market_cap: Optional[Decimal] = Field(default=None, decimal_places=0, description="Market capitalization in USD")
    market_cap_category: Optional[MarketCapEnum] = Field(default=None)

    # Price data
    current_price: Optional[Decimal] = Field(default=None, decimal_places=2)
    price_52week_high: Optional[Decimal] = Field(default=None, decimal_places=2)
    price_52week_low: Optional[Decimal] = Field(default=None, decimal_places=2)

    # Additional metrics
    debt_to_equity: Optional[Decimal] = Field(default=None, decimal_places=2)
    return_on_equity: Optional[Decimal] = Field(default=None, decimal_places=2)
    revenue_growth: Optional[Decimal] = Field(default=None, decimal_places=2)

    # Metadata
    is_active: bool = Field(default=True)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Additional data storage for future API integrations
    extra_data: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))

    # Relationships
    sector: Optional[Sector] = Relationship(back_populates="stocks")
    valuations: List["StockValuation"] = Relationship(back_populates="stock")


class StockValuation(SQLModel, table=True):
    """Historical valuation assessments and screening results"""

    __tablename__ = "stock_valuations"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    stock_id: int = Field(foreign_key="stocks.id")
    valuation_date: datetime = Field(default_factory=datetime.utcnow)

    # Valuation flags based on criteria
    is_undervalued_pe: bool = Field(default=False, description="PE ratio below sector average")
    is_undervalued_pb: bool = Field(default=False, description="PB ratio below 1.5")
    has_high_dividend: bool = Field(default=False, description="Dividend yield above 3%")
    overall_score: Decimal = Field(default=Decimal("0"), decimal_places=2, description="Overall valuation score 0-100")

    # Criteria thresholds used for this valuation
    pe_threshold: Optional[Decimal] = Field(default=None, decimal_places=2)
    pb_threshold: Decimal = Field(default=Decimal("1.5"), decimal_places=2)
    dividend_threshold: Decimal = Field(default=Decimal("3.0"), decimal_places=2)

    # Notes and reasoning
    notes: str = Field(default="", max_length=1000)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    stock: Stock = Relationship(back_populates="valuations")


class ValuationCriteria(SQLModel, table=True):
    """Configurable criteria for stock valuation screening"""

    __tablename__ = "valuation_criteria"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    description: str = Field(default="", max_length=500)

    # Threshold settings
    max_pe_ratio: Optional[Decimal] = Field(default=None, decimal_places=2)
    max_pb_ratio: Decimal = Field(default=Decimal("1.5"), decimal_places=2)
    min_dividend_yield: Decimal = Field(default=Decimal("3.0"), decimal_places=2)
    min_market_cap: Optional[Decimal] = Field(default=None, decimal_places=0)
    max_debt_to_equity: Optional[Decimal] = Field(default=None, decimal_places=2)
    min_roe: Optional[Decimal] = Field(default=None, decimal_places=2)

    # Sector-specific settings
    sector_specific: bool = Field(default=True, description="Use sector-specific PE thresholds")

    # Metadata
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Non-persistent schemas (for validation, forms, API requests/responses)
class StockCreate(SQLModel, table=False):
    """Schema for creating new stocks"""

    ticker: str = Field(max_length=10)
    company_name: str = Field(max_length=200)
    sector_id: Optional[int] = None
    industry: str = Field(max_length=100)

    pe_ratio: Optional[Decimal] = None
    pb_ratio: Optional[Decimal] = None
    dividend_yield: Optional[Decimal] = None
    market_cap: Optional[Decimal] = None
    current_price: Optional[Decimal] = None


class StockUpdate(SQLModel, table=False):
    """Schema for updating stock data"""

    company_name: Optional[str] = Field(default=None, max_length=200)
    sector_id: Optional[int] = None
    industry: Optional[str] = Field(default=None, max_length=100)

    pe_ratio: Optional[Decimal] = None
    pb_ratio: Optional[Decimal] = None
    dividend_yield: Optional[Decimal] = None
    market_cap: Optional[Decimal] = None
    current_price: Optional[Decimal] = None
    price_52week_high: Optional[Decimal] = None
    price_52week_low: Optional[Decimal] = None
    debt_to_equity: Optional[Decimal] = None
    return_on_equity: Optional[Decimal] = None
    revenue_growth: Optional[Decimal] = None

    is_active: Optional[bool] = None


class StockFilter(SQLModel, table=False):
    """Schema for filtering stocks"""

    sector_id: Optional[int] = None
    industry: Optional[str] = None
    market_cap_category: Optional[MarketCapEnum] = None

    max_pe_ratio: Optional[Decimal] = None
    max_pb_ratio: Optional[Decimal] = None
    min_dividend_yield: Optional[Decimal] = None
    min_market_cap: Optional[Decimal] = None
    max_market_cap: Optional[Decimal] = None

    ticker_search: Optional[str] = Field(default=None, max_length=50)
    company_search: Optional[str] = Field(default=None, max_length=200)

    is_active: Optional[bool] = True


class StockSort(SQLModel, table=False):
    """Schema for sorting stocks"""

    field: str = Field(description="Field to sort by")
    direction: str = Field(default="asc", regex="^(asc|desc)$")


class SectorCreate(SQLModel, table=False):
    """Schema for creating sectors"""

    name: str = Field(max_length=100)
    description: str = Field(default="", max_length=500)
    average_pe_ratio: Optional[Decimal] = None
    average_pb_ratio: Optional[Decimal] = None
    average_dividend_yield: Optional[Decimal] = None


class ValuationCriteriaCreate(SQLModel, table=False):
    """Schema for creating valuation criteria"""

    name: str = Field(max_length=100)
    description: str = Field(default="", max_length=500)
    max_pe_ratio: Optional[Decimal] = None
    max_pb_ratio: Decimal = Field(default=Decimal("1.5"))
    min_dividend_yield: Decimal = Field(default=Decimal("3.0"))
    min_market_cap: Optional[Decimal] = None
    max_debt_to_equity: Optional[Decimal] = None
    min_roe: Optional[Decimal] = None
    sector_specific: bool = Field(default=True)


class StockScreenResult(SQLModel, table=False):
    """Schema for stock screening results"""

    stock_id: int
    ticker: str
    company_name: str
    sector_name: Optional[str] = None
    industry: str

    pe_ratio: Optional[Decimal] = None
    pb_ratio: Optional[Decimal] = None
    dividend_yield: Optional[Decimal] = None
    market_cap: Optional[Decimal] = None
    current_price: Optional[Decimal] = None

    is_undervalued_pe: bool = False
    is_undervalued_pb: bool = False
    has_high_dividend: bool = False
    overall_score: Decimal = Field(default=Decimal("0"))

    last_updated: str  # ISO format datetime string
