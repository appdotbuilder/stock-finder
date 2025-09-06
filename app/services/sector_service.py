from typing import List, Optional
from sqlmodel import select
from decimal import Decimal

from app.database import get_session
from app.models import Sector, SectorCreate


class SectorService:
    """Service for sector operations"""

    @staticmethod
    def get_all_sectors() -> List[Sector]:
        """Get all sectors"""
        with get_session() as session:
            statement = select(Sector).order_by(Sector.name)
            return list(session.exec(statement).all())

    @staticmethod
    def get_sector_by_id(sector_id: int) -> Optional[Sector]:
        """Get sector by ID"""
        with get_session() as session:
            return session.get(Sector, sector_id)

    @staticmethod
    def get_sector_by_name(name: str) -> Optional[Sector]:
        """Get sector by name"""
        with get_session() as session:
            statement = select(Sector).where(Sector.name == name)
            return session.exec(statement).first()

    @staticmethod
    def create_sector(sector_data: SectorCreate) -> Sector:
        """Create a new sector"""
        with get_session() as session:
            sector = Sector(**sector_data.model_dump())
            session.add(sector)
            session.commit()
            session.refresh(sector)
            return sector

    @staticmethod
    def create_default_sectors() -> List[Sector]:
        """Create default sectors with industry averages"""
        default_sectors = [
            {
                "name": "Technology",
                "description": "Software, hardware, and technology services companies",
                "average_pe_ratio": Decimal("28.5"),
                "average_pb_ratio": Decimal("4.2"),
                "average_dividend_yield": Decimal("1.8"),
            },
            {
                "name": "Healthcare",
                "description": "Pharmaceutical, biotechnology, and medical device companies",
                "average_pe_ratio": Decimal("22.3"),
                "average_pb_ratio": Decimal("3.1"),
                "average_dividend_yield": Decimal("2.4"),
            },
            {
                "name": "Financials",
                "description": "Banks, insurance companies, and financial services",
                "average_pe_ratio": Decimal("12.8"),
                "average_pb_ratio": Decimal("1.1"),
                "average_dividend_yield": Decimal("3.2"),
            },
            {
                "name": "Consumer Discretionary",
                "description": "Retail, automotive, and entertainment companies",
                "average_pe_ratio": Decimal("18.7"),
                "average_pb_ratio": Decimal("2.8"),
                "average_dividend_yield": Decimal("2.1"),
            },
            {
                "name": "Consumer Staples",
                "description": "Food, beverage, and household product companies",
                "average_pe_ratio": Decimal("19.4"),
                "average_pb_ratio": Decimal("3.5"),
                "average_dividend_yield": Decimal("2.8"),
            },
            {
                "name": "Industrials",
                "description": "Manufacturing, aerospace, and industrial services",
                "average_pe_ratio": Decimal("16.9"),
                "average_pb_ratio": Decimal("2.1"),
                "average_dividend_yield": Decimal("2.5"),
            },
            {
                "name": "Energy",
                "description": "Oil, gas, and renewable energy companies",
                "average_pe_ratio": Decimal("14.2"),
                "average_pb_ratio": Decimal("1.3"),
                "average_dividend_yield": Decimal("4.1"),
            },
            {
                "name": "Materials",
                "description": "Mining, chemicals, and construction materials",
                "average_pe_ratio": Decimal("15.6"),
                "average_pb_ratio": Decimal("1.8"),
                "average_dividend_yield": Decimal("3.0"),
            },
            {
                "name": "Utilities",
                "description": "Electric, gas, and water utility companies",
                "average_pe_ratio": Decimal("18.3"),
                "average_pb_ratio": Decimal("1.4"),
                "average_dividend_yield": Decimal("3.8"),
            },
            {
                "name": "Real Estate",
                "description": "REITs and real estate development companies",
                "average_pe_ratio": Decimal("25.1"),
                "average_pb_ratio": Decimal("1.2"),
                "average_dividend_yield": Decimal("4.3"),
            },
        ]

        created_sectors = []
        with get_session() as session:
            for sector_data in default_sectors:
                # Check if sector already exists
                existing = session.exec(select(Sector).where(Sector.name == sector_data["name"])).first()

                if not existing:
                    sector = Sector(**sector_data)
                    session.add(sector)
                    created_sectors.append(sector)

            if created_sectors:
                session.commit()
                for sector in created_sectors:
                    session.refresh(sector)

        return created_sectors
