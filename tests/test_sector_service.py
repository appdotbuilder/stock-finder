import pytest
from decimal import Decimal

from app.database import reset_db
from app.services.sector_service import SectorService
from app.models import SectorCreate


@pytest.fixture()
def fresh_db():
    """Provide a fresh database for each test"""
    reset_db()
    yield
    reset_db()


class TestSectorService:
    """Test cases for SectorService"""

    def test_get_all_sectors_empty(self, fresh_db):
        """Test getting sectors from empty database"""
        sectors = SectorService.get_all_sectors()
        assert sectors == []

    def test_create_sector(self, fresh_db):
        """Test creating a sector"""
        sector_data = SectorCreate(
            name="Test Sector",
            description="A test sector",
            average_pe_ratio=Decimal("20.5"),
            average_pb_ratio=Decimal("3.2"),
            average_dividend_yield=Decimal("2.1"),
        )

        sector = SectorService.create_sector(sector_data)

        assert sector.name == "Test Sector"
        assert sector.description == "A test sector"
        assert sector.average_pe_ratio == Decimal("20.5")
        assert sector.average_pb_ratio == Decimal("3.2")
        assert sector.average_dividend_yield == Decimal("2.1")
        assert sector.id is not None
        assert sector.created_at is not None

    def test_get_sector_by_name(self, fresh_db):
        """Test getting sector by name"""
        sector_data = SectorCreate(name="Technology", description="Tech companies")
        created_sector = SectorService.create_sector(sector_data)

        # Test existing sector
        found_sector = SectorService.get_sector_by_name("Technology")
        assert found_sector is not None
        assert found_sector.name == "Technology"
        assert found_sector.id == created_sector.id

        # Test non-existent sector
        missing_sector = SectorService.get_sector_by_name("Non-existent")
        assert missing_sector is None

    def test_get_sector_by_id(self, fresh_db):
        """Test getting sector by ID"""
        sector_data = SectorCreate(name="Healthcare")
        created_sector = SectorService.create_sector(sector_data)

        # Test existing sector
        if created_sector.id is not None:
            found_sector = SectorService.get_sector_by_id(created_sector.id)
            assert found_sector is not None
            assert found_sector.name == "Healthcare"
            assert found_sector.id == created_sector.id

        # Test non-existent ID
        missing_sector = SectorService.get_sector_by_id(99999)
        assert missing_sector is None

    def test_create_default_sectors(self, fresh_db):
        """Test creating default sectors"""
        sectors = SectorService.create_default_sectors()

        assert len(sectors) == 10  # Should create 10 default sectors

        # Check that all expected sectors were created
        sector_names = [s.name for s in sectors]
        expected_sectors = [
            "Technology",
            "Healthcare",
            "Financials",
            "Consumer Discretionary",
            "Consumer Staples",
            "Industrials",
            "Energy",
            "Materials",
            "Utilities",
            "Real Estate",
        ]

        for expected in expected_sectors:
            assert expected in sector_names

        # Verify some sector details
        tech_sector = next((s for s in sectors if s.name == "Technology"), None)
        assert tech_sector is not None
        assert tech_sector.description == "Software, hardware, and technology services companies"
        assert tech_sector.average_pe_ratio == Decimal("28.5")
        assert tech_sector.average_pb_ratio == Decimal("4.2")
        assert tech_sector.average_dividend_yield == Decimal("1.8")

        # Verify financials sector (important for undervalued screening)
        finance_sector = next((s for s in sectors if s.name == "Financials"), None)
        assert finance_sector is not None
        assert finance_sector.average_pe_ratio == Decimal("12.8")
        assert finance_sector.average_pb_ratio == Decimal("1.1")
        assert finance_sector.average_dividend_yield == Decimal("3.2")

    def test_create_default_sectors_no_duplicates(self, fresh_db):
        """Test that creating default sectors twice doesn't create duplicates"""
        # Create default sectors first time
        first_run = SectorService.create_default_sectors()
        assert len(first_run) == 10

        # Create default sectors second time
        second_run = SectorService.create_default_sectors()
        assert len(second_run) == 0  # Should not create duplicates

        # Verify total count is still 10
        all_sectors = SectorService.get_all_sectors()
        assert len(all_sectors) == 10

    def test_sectors_ordered_by_name(self, fresh_db):
        """Test that sectors are returned ordered by name"""
        # Create sectors in non-alphabetical order
        SectorService.create_sector(SectorCreate(name="Zebra"))
        SectorService.create_sector(SectorCreate(name="Alpha"))
        SectorService.create_sector(SectorCreate(name="Beta"))

        sectors = SectorService.get_all_sectors()
        sector_names = [s.name for s in sectors]

        assert sector_names == ["Alpha", "Beta", "Zebra"]

    def test_create_sector_with_minimal_data(self, fresh_db):
        """Test creating sector with only required fields"""
        sector_data = SectorCreate(name="Minimal Sector")
        sector = SectorService.create_sector(sector_data)

        assert sector.name == "Minimal Sector"
        assert sector.description == ""  # Default empty description
        assert sector.average_pe_ratio is None
        assert sector.average_pb_ratio is None
        assert sector.average_dividend_yield is None

    def test_create_sector_with_all_data(self, fresh_db):
        """Test creating sector with all fields populated"""
        sector_data = SectorCreate(
            name="Complete Sector",
            description="A sector with all data",
            average_pe_ratio=Decimal("15.5"),
            average_pb_ratio=Decimal("2.1"),
            average_dividend_yield=Decimal("3.8"),
        )

        sector = SectorService.create_sector(sector_data)

        assert sector.name == "Complete Sector"
        assert sector.description == "A sector with all data"
        assert sector.average_pe_ratio == Decimal("15.5")
        assert sector.average_pb_ratio == Decimal("2.1")
        assert sector.average_dividend_yield == Decimal("3.8")

    def test_sector_relationships_ready(self, fresh_db):
        """Test that created sectors are ready for stock relationships"""
        sectors = SectorService.create_default_sectors()

        # All sectors should have valid IDs for foreign key relationships
        for sector in sectors:
            assert sector.id is not None
            assert isinstance(sector.id, int)
            assert sector.id > 0
