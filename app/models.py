from sqlalchemy import Column, Integer, String, Double, DateTime, BigInteger
from app.database import Base
from datetime import datetime, timezone

class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(200), nullable=False, unique=True)
    capital = Column(String(200), nullable=True)
    region = Column(String(50), nullable=True)
    population = Column(BigInteger, nullable=False)
    currency_code = Column(String(3), nullable=True, default=None)
    exchange_rate = Column(Double, nullable=True, default=None)
    estimated_gdp = Column(Double, nullable=True, default=0)

    flag_url = Column(String(100), nullable=True)
    last_refreshed_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc), nullable=False
    )