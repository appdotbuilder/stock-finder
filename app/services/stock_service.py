from typing import List, Optional, Tuple
from sqlmodel import select
from decimal import Decimal
import logging

from app.database import get_session
from app.models import Stock, Sector, StockCreate, StockFilter, StockSort, StockScreenResult, MarketCapEnum

logger = logging.getLogger(__name__)


class StockService:
    """Simplified service for stock operations and screening"""

    @staticmethod
    def get_all_stocks() -> List[Stock]:
        """Get all active stocks"""
        with get_session() as session:
            statement = select(Stock).where(Stock.is_active == True)  # noqa: E712
            return list(session.exec(statement).all())

    @staticmethod
    def get_stock_by_ticker(ticker: str) -> Optional[Stock]:
        """Get stock by ticker symbol"""
        with get_session() as session:
            statement = select(Stock).where(Stock.ticker == ticker.upper())
            return session.exec(statement).first()

    @staticmethod
    def create_stock(stock_data: StockCreate) -> Stock:
        """Create a new stock"""
        with get_session() as session:
            # Determine market cap category
            market_cap_category = None
            if stock_data.market_cap:
                if stock_data.market_cap >= 10_000_000_000:  # > $10B
                    market_cap_category = MarketCapEnum.LARGE_CAP
                elif stock_data.market_cap >= 2_000_000_000:  # $2B - $10B
                    market_cap_category = MarketCapEnum.MID_CAP
                elif stock_data.market_cap >= 300_000_000:  # $300M - $2B
                    market_cap_category = MarketCapEnum.SMALL_CAP
                else:  # < $300M
                    market_cap_category = MarketCapEnum.MICRO_CAP

            stock = Stock(
                ticker=stock_data.ticker.upper(),
                company_name=stock_data.company_name,
                sector_id=stock_data.sector_id,
                industry=stock_data.industry,
                pe_ratio=stock_data.pe_ratio,
                pb_ratio=stock_data.pb_ratio,
                dividend_yield=stock_data.dividend_yield,
                market_cap=stock_data.market_cap,
                market_cap_category=market_cap_category,
                current_price=stock_data.current_price,
            )
            session.add(stock)
            session.commit()
            session.refresh(stock)
            return stock

    @staticmethod
    def search_and_filter_stocks(
        filters: Optional[StockFilter] = None, sort_by: Optional[StockSort] = None, limit: int = 100, offset: int = 0
    ) -> Tuple[List[Stock], int]:
        """Search and filter stocks with basic filtering"""
        with get_session() as session:
            # Start with all active stocks
            all_stocks = list(
                session.exec(
                    select(Stock).where(Stock.is_active == True)  # noqa: E712
                ).all()
            )

            # Apply client-side filtering for simplicity
            filtered_stocks = []

            for stock in all_stocks:
                include = True

                if filters:
                    # Ticker search
                    if filters.ticker_search and filters.ticker_search.upper() not in stock.ticker:
                        include = False
                        continue

                    # Company search
                    if filters.company_search and filters.company_search.lower() not in stock.company_name.lower():
                        include = False
                        continue

                    # Sector filter
                    if filters.sector_id is not None and stock.sector_id != filters.sector_id:
                        include = False
                        continue

                    # Market cap category filter
                    if filters.market_cap_category and stock.market_cap_category != filters.market_cap_category:
                        include = False
                        continue

                    # P/E ratio filter
                    if filters.max_pe_ratio is not None:
                        if stock.pe_ratio is not None and stock.pe_ratio > filters.max_pe_ratio:
                            include = False
                            continue

                    # P/B ratio filter
                    if filters.max_pb_ratio is not None:
                        if stock.pb_ratio is not None and stock.pb_ratio > filters.max_pb_ratio:
                            include = False
                            continue

                    # Dividend yield filter
                    if filters.min_dividend_yield is not None:
                        if stock.dividend_yield is None or stock.dividend_yield < filters.min_dividend_yield:
                            include = False
                            continue

                if include:
                    filtered_stocks.append(stock)

            # Apply sorting
            if sort_by and sort_by.field:

                def sort_key(stock):
                    value = getattr(stock, sort_by.field, None)
                    if value is None:
                        return float("inf") if sort_by.direction == "asc" else float("-inf")
                    return float(value) if isinstance(value, Decimal) else value

                filtered_stocks.sort(key=sort_key, reverse=(sort_by.direction == "desc"))

            total_count = len(filtered_stocks)

            # Apply pagination
            start_idx = offset
            end_idx = offset + limit
            paginated_stocks = filtered_stocks[start_idx:end_idx]

            return paginated_stocks, total_count

    @staticmethod
    def screen_undervalued_stocks(criteria_id: Optional[int] = None) -> List[StockScreenResult]:
        """Screen stocks based on undervaluation criteria"""
        with get_session() as session:
            # Use default criteria for simplicity
            max_pb = Decimal("1.5")
            min_dividend = Decimal("3.0")

            # Get all stocks with their sectors
            stocks = session.exec(select(Stock).where(Stock.is_active == True)).all()  # noqa: E712
            sectors = {s.id: s for s in session.exec(select(Sector)).all()}

            screen_results = []

            for stock in stocks:
                # Calculate undervaluation flags
                is_undervalued_pe = False
                is_undervalued_pb = False
                has_high_dividend = False

                # PE ratio check (compare to sector average if available)
                if stock.pe_ratio is not None and stock.sector_id:
                    sector = sectors.get(stock.sector_id)
                    if sector and sector.average_pe_ratio:
                        is_undervalued_pe = stock.pe_ratio < sector.average_pe_ratio

                # PB ratio check
                if stock.pb_ratio is not None:
                    is_undervalued_pb = stock.pb_ratio < max_pb

                # Dividend yield check
                if stock.dividend_yield is not None:
                    has_high_dividend = stock.dividend_yield >= min_dividend

                # Calculate overall score (0-100)
                score = 0
                if is_undervalued_pe:
                    score += 40
                if is_undervalued_pb:
                    score += 40
                if has_high_dividend:
                    score += 20

                overall_score = Decimal(str(score))

                # Only include stocks that meet at least one criterion
                if overall_score > 0:
                    sector_name = None
                    if stock.sector_id and stock.sector_id in sectors:
                        sector_name = sectors[stock.sector_id].name

                    screen_results.append(
                        StockScreenResult(
                            stock_id=stock.id or 0,
                            ticker=stock.ticker,
                            company_name=stock.company_name,
                            sector_name=sector_name,
                            industry=stock.industry,
                            pe_ratio=stock.pe_ratio,
                            pb_ratio=stock.pb_ratio,
                            dividend_yield=stock.dividend_yield,
                            market_cap=stock.market_cap,
                            current_price=stock.current_price,
                            is_undervalued_pe=is_undervalued_pe,
                            is_undervalued_pb=is_undervalued_pb,
                            has_high_dividend=has_high_dividend,
                            overall_score=overall_score,
                            last_updated=stock.last_updated.isoformat(),
                        )
                    )

            # Sort by overall score descending
            screen_results.sort(key=lambda x: x.overall_score, reverse=True)
            return screen_results

    @staticmethod
    def get_available_sectors() -> List[Sector]:
        """Get all available sectors"""
        with get_session() as session:
            statement = select(Sector).order_by(Sector.name)
            return list(session.exec(statement).all())

    @staticmethod
    def get_available_industries() -> List[str]:
        """Get unique industries from stocks"""
        with get_session() as session:
            stocks = session.exec(select(Stock).where(Stock.is_active == True)).all()  # noqa: E712
            industries = {stock.industry for stock in stocks if stock.industry}
            return sorted(list(industries))

    @staticmethod
    def get_stock_statistics() -> dict:
        """Get basic statistics about the stock database"""
        with get_session() as session:
            stocks = list(
                session.exec(
                    select(Stock).where(Stock.is_active == True)  # noqa: E712
                ).all()
            )

            total_count = len(stocks)
            pe_count = len([s for s in stocks if s.pe_ratio is not None])
            pb_count = len([s for s in stocks if s.pb_ratio is not None])
            div_count = len([s for s in stocks if s.dividend_yield is not None])

            return {
                "total_stocks": total_count,
                "with_pe_ratio": pe_count,
                "with_pb_ratio": pb_count,
                "with_dividend_yield": div_count,
            }
