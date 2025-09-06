from nicegui import ui
from decimal import Decimal
import logging

from app.services.stock_service import StockService
from app.services.sector_service import SectorService
from app.services.mock_data_service import MockDataService
from app.models import StockFilter, StockSort, MarketCapEnum

logger = logging.getLogger(__name__)


class StockScreener:
    """Main stock screener interface"""

    def __init__(self):
        self.current_stocks = []
        self.current_filters = StockFilter()
        self.current_sort = StockSort(field="overall_score", direction="desc")
        self.stock_table = None
        self.stats_container = None

    def create_filters_section(self):
        """Create the filters section"""
        with ui.card().classes("w-full p-4 mb-4"):
            ui.label("Stock Filters").classes("text-lg font-semibold mb-3")

            with ui.row().classes("gap-4 w-full items-end"):
                # Ticker search
                ticker_input = ui.input("Ticker Search", placeholder="e.g., AAPL").classes("w-32")

                # Company search
                company_input = ui.input("Company Search", placeholder="e.g., Apple").classes("w-48")

                # Sector filter
                sectors = SectorService.get_all_sectors()
                sector_options = ["All Sectors"] + [s.name for s in sectors]
                sector_select = ui.select(sector_options, label="Sector", value="All Sectors").classes("w-40")

                # Market cap filter
                mcap_options = ["All Sizes"] + [e.value for e in MarketCapEnum]
                mcap_select = ui.select(mcap_options, label="Market Cap", value="All Sizes").classes("w-32")

            with ui.row().classes("gap-4 w-full items-end mt-3"):
                # Valuation filters
                max_pe_input = ui.number("Max P/E Ratio", placeholder="e.g., 15", format="%.1f").classes("w-32")

                max_pb_input = ui.number("Max P/B Ratio", placeholder="e.g., 1.5", format="%.1f").classes("w-32")

                min_div_input = ui.number("Min Dividend Yield %", placeholder="e.g., 3.0", format="%.1f").classes(
                    "w-40"
                )

                # Action buttons
                ui.button("Apply Filters", on_click=self.apply_filters).classes("bg-blue-500 text-white px-4 py-2")

                ui.button("Clear", on_click=self.clear_filters).classes("bg-gray-400 text-white px-4 py-2")

                ui.button("Find Undervalued", on_click=self.screen_undervalued).classes(
                    "bg-green-500 text-white px-4 py-2 font-semibold"
                )

        # Store references for filter application
        self.ticker_input = ticker_input
        self.company_input = company_input
        self.sector_select = sector_select
        self.mcap_select = mcap_select
        self.max_pe_input = max_pe_input
        self.max_pb_input = max_pb_input
        self.min_div_input = min_div_input

    def create_stats_section(self):
        """Create the statistics section"""
        with ui.card().classes("w-full p-4 mb-4") as stats_card:
            with ui.row().classes("gap-8 w-full justify-around"):
                self.stats_container = stats_card
                self.update_stats()

    def update_stats(self):
        """Update statistics display"""
        if not self.stats_container:
            return

        with self.stats_container:
            self.stats_container.clear()
            ui.label("Database Statistics").classes("text-lg font-semibold mb-3 w-full")

            stats = StockService.get_stock_statistics()

            with ui.row().classes("gap-8 w-full justify-around"):
                # Total stocks
                with ui.column().classes("text-center"):
                    ui.label(str(stats["total_stocks"])).classes("text-3xl font-bold text-blue-600")
                    ui.label("Total Stocks").classes("text-sm text-gray-600")

                # With PE ratio
                with ui.column().classes("text-center"):
                    ui.label(str(stats["with_pe_ratio"])).classes("text-3xl font-bold text-green-600")
                    ui.label("With P/E Ratio").classes("text-sm text-gray-600")

                # With PB ratio
                with ui.column().classes("text-center"):
                    ui.label(str(stats["with_pb_ratio"])).classes("text-3xl font-bold text-purple-600")
                    ui.label("With P/B Ratio").classes("text-sm text-gray-600")

                # With dividend
                with ui.column().classes("text-center"):
                    ui.label(str(stats["with_dividend_yield"])).classes("text-3xl font-bold text-orange-600")
                    ui.label("With Dividend").classes("text-sm text-gray-600")

                # Current results
                with ui.column().classes("text-center"):
                    ui.label(str(len(self.current_stocks))).classes("text-3xl font-bold text-red-600")
                    ui.label("Current Results").classes("text-sm text-gray-600")

    def create_table_section(self):
        """Create the stock table section"""
        with ui.card().classes("w-full p-4"):
            ui.label("Stock Analysis Results").classes("text-lg font-semibold mb-3")

            # Table container
            self.table_container = ui.column().classes("w-full")
            self.update_table()

    def update_table(self):
        """Update the stock table"""
        if not self.table_container:
            return

        with self.table_container:
            self.table_container.clear()

            if not self.current_stocks:
                ui.label("No stocks found matching current criteria").classes("text-gray-500 text-center py-8")
                return

            # Prepare table data
            rows = []
            for stock in self.current_stocks:
                # Handle None values gracefully
                pe_display = f"{float(stock.pe_ratio):.1f}" if stock.pe_ratio else "N/A"
                pb_display = f"{float(stock.pb_ratio):.1f}" if stock.pb_ratio else "N/A"
                div_display = f"{float(stock.dividend_yield):.1f}%" if stock.dividend_yield else "N/A"
                mcap_display = self.format_market_cap(stock.market_cap) if stock.market_cap else "N/A"
                price_display = f"${float(stock.current_price):.2f}" if stock.current_price else "N/A"

                # Get sector name
                sector_name = "N/A"
                if hasattr(stock, "sector") and stock.sector:
                    sector_name = stock.sector.name
                elif stock.sector_id:
                    sector = SectorService.get_sector_by_id(stock.sector_id)
                    if sector:
                        sector_name = sector.name

                rows.append(
                    {
                        "ticker": stock.ticker,
                        "company": stock.company_name,
                        "sector": sector_name,
                        "industry": stock.industry,
                        "pe_ratio": pe_display,
                        "pb_ratio": pb_display,
                        "dividend": div_display,
                        "market_cap": mcap_display,
                        "price": price_display,
                        "pe_sort": float(stock.pe_ratio) if stock.pe_ratio else 999999,
                        "pb_sort": float(stock.pb_ratio) if stock.pb_ratio else 999999,
                        "div_sort": float(stock.dividend_yield) if stock.dividend_yield else 0,
                        "mcap_sort": float(stock.market_cap) if stock.market_cap else 0,
                    }
                )

            # Define columns with sorting
            columns = [
                {
                    "name": "ticker",
                    "label": "Ticker",
                    "field": "ticker",
                    "sortable": True,
                    "classes": "font-mono font-bold text-blue-600",
                },
                {
                    "name": "company",
                    "label": "Company",
                    "field": "company",
                    "sortable": True,
                    "classes": "max-w-xs truncate",
                },
                {"name": "sector", "label": "Sector", "field": "sector", "sortable": True},
                {
                    "name": "pe_ratio",
                    "label": "P/E",
                    "field": "pe_ratio",
                    "sortable": True,
                    "sort_field": "pe_sort",
                    "align": "right",
                },
                {
                    "name": "pb_ratio",
                    "label": "P/B",
                    "field": "pb_ratio",
                    "sortable": True,
                    "sort_field": "pb_sort",
                    "align": "right",
                },
                {
                    "name": "dividend",
                    "label": "Div Yield",
                    "field": "dividend",
                    "sortable": True,
                    "sort_field": "div_sort",
                    "align": "right",
                },
                {
                    "name": "market_cap",
                    "label": "Market Cap",
                    "field": "market_cap",
                    "sortable": True,
                    "sort_field": "mcap_sort",
                    "align": "right",
                },
                {"name": "price", "label": "Price", "field": "price", "sortable": True, "align": "right"},
            ]

            # Create sortable table
            table = ui.table(columns=columns, rows=rows, row_key="ticker").classes("w-full")

            # Style the table
            table.props("dense flat bordered")

            # Add click handler for row selection
            table.on("rowClick", self.on_row_click)

            self.stock_table = table

    def format_market_cap(self, market_cap: Decimal) -> str:
        """Format market cap for display"""
        if not market_cap:
            return "N/A"

        value = float(market_cap)
        if value >= 1e12:
            return f"${value / 1e12:.1f}T"
        elif value >= 1e9:
            return f"${value / 1e9:.1f}B"
        elif value >= 1e6:
            return f"${value / 1e6:.1f}M"
        else:
            return f"${value:,.0f}"

    def on_row_click(self, e):
        """Handle row click events"""
        ticker = e.args[1]["ticker"]
        ui.notify(f"Selected stock: {ticker}", type="info")

    def apply_filters(self):
        """Apply current filter settings"""
        try:
            # Build filter object
            filters = StockFilter()

            # Ticker search
            if self.ticker_input.value:
                filters.ticker_search = self.ticker_input.value.strip()

            # Company search
            if self.company_input.value:
                filters.company_search = self.company_input.value.strip()

            # Sector filter
            if self.sector_select.value and self.sector_select.value != "All Sectors":
                sectors = SectorService.get_all_sectors()
                sector_lookup = {s.name: s.id for s in sectors}
                filters.sector_id = sector_lookup.get(self.sector_select.value)

            # Market cap filter
            if self.mcap_select.value and self.mcap_select.value != "All Sizes":
                filters.market_cap_category = MarketCapEnum(self.mcap_select.value)

            # Valuation filters
            if self.max_pe_input.value:
                filters.max_pe_ratio = Decimal(str(self.max_pe_input.value))

            if self.max_pb_input.value:
                filters.max_pb_ratio = Decimal(str(self.max_pb_input.value))

            if self.min_div_input.value:
                filters.min_dividend_yield = Decimal(str(self.min_div_input.value))

            # Apply filters
            self.current_filters = filters
            stocks, total = StockService.search_and_filter_stocks(filters, limit=200)
            self.current_stocks = stocks

            # Update display
            self.update_table()
            self.update_stats()

            ui.notify(f"Found {len(stocks)} stocks matching criteria", type="positive")

        except Exception as e:
            logger.error(f"Error applying filters: {str(e)}")
            ui.notify(f"Error applying filters: {str(e)}", type="negative")

    def clear_filters(self):
        """Clear all filters"""
        try:
            # Reset filter inputs
            self.ticker_input.set_value("")
            self.company_input.set_value("")
            self.sector_select.set_value("All Sectors")
            self.mcap_select.set_value("All Sizes")
            self.max_pe_input.set_value(None)
            self.max_pb_input.set_value(None)
            self.min_div_input.set_value(None)

            # Load all stocks
            self.current_filters = StockFilter()
            stocks, total = StockService.search_and_filter_stocks(limit=200)
            self.current_stocks = stocks

            # Update display
            self.update_table()
            self.update_stats()

            ui.notify("Filters cleared", type="info")

        except Exception as e:
            logger.error(f"Error clearing filters: {str(e)}")
            ui.notify(f"Error clearing filters: {str(e)}", type="negative")

    def screen_undervalued(self):
        """Screen for undervalued stocks"""
        try:
            screen_results = StockService.screen_undervalued_stocks()

            if not screen_results:
                ui.notify("No undervalued stocks found with current criteria", type="warning")
                return

            # Convert screen results to stock objects for display
            # Note: This is a simplified approach - in a real app you might want
            # to create a separate table for screening results
            stock_ids = [result.stock_id for result in screen_results]

            # Get full stock objects
            all_stocks = StockService.get_all_stocks()
            undervalued_stocks = [stock for stock in all_stocks if stock.id in stock_ids]

            # Sort by the screening score (we'll approximate this by combining criteria)
            def score_stock(stock):
                score = 0
                if stock.pe_ratio and stock.sector_id:
                    sector = SectorService.get_sector_by_id(stock.sector_id)
                    if sector and sector.average_pe_ratio and stock.pe_ratio < sector.average_pe_ratio:
                        score += 40

                if stock.pb_ratio and stock.pb_ratio < Decimal("1.5"):
                    score += 40

                if stock.dividend_yield and stock.dividend_yield >= Decimal("3.0"):
                    score += 20

                return score

            undervalued_stocks.sort(key=score_stock, reverse=True)

            self.current_stocks = undervalued_stocks
            self.update_table()
            self.update_stats()

            ui.notify(f"Found {len(undervalued_stocks)} undervalued stocks!", type="positive")

        except Exception as e:
            logger.error(f"Error screening stocks: {str(e)}")
            ui.notify(f"Error screening stocks: {str(e)}", type="negative")

    def load_initial_data(self):
        """Load initial data for the screener"""
        try:
            # Load all stocks initially
            stocks, total = StockService.search_and_filter_stocks(limit=200)
            self.current_stocks = stocks

            if len(stocks) < 10:
                # Initialize with mock data if database is empty
                ui.notify("Initializing database with sample data...", type="info")
                MockDataService.initialize_database()
                stocks, total = StockService.search_and_filter_stocks(limit=200)
                self.current_stocks = stocks

            ui.notify(f"Loaded {len(stocks)} stocks", type="positive")

        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            ui.notify(f"Error loading data: {str(e)}", type="negative")
            self.current_stocks = []


def create():
    """Create the stock screener application"""

    # Apply modern theme colors
    ui.colors(
        primary="#2563eb",  # Professional blue
        secondary="#64748b",  # Subtle gray
        accent="#10b981",  # Success green
        positive="#10b981",
        negative="#ef4444",  # Error red
        warning="#f59e0b",  # Warning amber
        info="#3b82f6",  # Info blue
    )

    @ui.page("/")
    def index():
        """Main stock screener page"""

        # Page header
        with ui.row().classes("w-full items-center justify-between mb-6"):
            ui.label("Stock Value Screener").classes("text-3xl font-bold text-gray-800")
            ui.label("Find undervalued stocks using P/E, P/B, and dividend criteria").classes("text-lg text-gray-600")

        # Create screener instance
        screener = StockScreener()

        # Create UI sections
        screener.create_stats_section()
        screener.create_filters_section()
        screener.create_table_section()

        # Load initial data
        screener.load_initial_data()

        # Update display
        screener.update_table()
        screener.update_stats()

    @ui.page("/admin")
    def admin():
        """Admin page for data management"""

        ui.label("Stock Screener Admin").classes("text-2xl font-bold mb-4")

        with ui.card().classes("p-4 mb-4"):
            ui.label("Database Management").classes("text-lg font-semibold mb-3")

            with ui.row().classes("gap-4"):

                def init_data():
                    try:
                        MockDataService.initialize_database()
                        ui.notify("Database initialized successfully!", type="positive")
                    except Exception as e:
                        logger.error(f"Error initializing database: {str(e)}")
                        ui.notify(f"Error initializing database: {str(e)}", type="negative")

                def show_stats():
                    stats = StockService.get_stock_statistics()
                    ui.notify(f"Stats: {stats['total_stocks']} total stocks", type="info")

                ui.button("Initialize Sample Data", on_click=init_data).classes("bg-blue-500 text-white px-4 py-2")
                ui.button("Show Statistics", on_click=show_stats).classes("bg-gray-500 text-white px-4 py-2")

        # Show current statistics
        with ui.card().classes("p-4"):
            ui.label("Current Database Status").classes("text-lg font-semibold mb-3")

            try:
                stats = StockService.get_stock_statistics()
                with ui.column().classes("gap-2"):
                    ui.label(f"Total Stocks: {stats['total_stocks']}")
                    ui.label(f"Stocks with P/E Ratio: {stats['with_pe_ratio']}")
                    ui.label(f"Stocks with P/B Ratio: {stats['with_pb_ratio']}")
                    ui.label(f"Stocks with Dividend Yield: {stats['with_dividend_yield']}")
            except Exception as e:
                logger.error(f"Error loading statistics: {str(e)}")
                ui.label(f"Error loading statistics: {str(e)}").classes("text-red-500")
