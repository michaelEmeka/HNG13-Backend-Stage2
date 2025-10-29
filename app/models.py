from sqlalchemy import Column, Integer, String, Double, DateTime, BigInteger
from app.database import Base
from datetime import datetime, timezone
from sqlalchemy.sql import func
from sqlalchemy import text

class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(200), nullable=False, unique=True, index=True)
    capital = Column(String(200), nullable=True)
    region = Column(String(50), nullable=True)
    population = Column(BigInteger, nullable=False)
    currency_code = Column(String(3), nullable=True, default=None)
    exchange_rate = Column(Double, nullable=True, default=None)
    estimated_gdp = Column(Double, nullable=True, default=0)

    flag_url = Column(String(100), nullable=True)
    last_refreshed_at = Column(
        DateTime(timezone=True),
        # default=func.now(),
        server_default=func.now(),  # set current time at creation
        server_onupdate=func.now(),  # update automatically on any change
        onupdate=func.now(),
        nullable=False
        # server_onupdate=text("CURRENT_TIMESTAMP")
    )
    print(func.now())
