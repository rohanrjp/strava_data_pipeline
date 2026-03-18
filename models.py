from datetime import datetime
from sqlalchemy import BigInteger, String, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from database import Base
from sqlalchemy.dialects.postgresql import JSONB


class StravaCredentials(Base):
    __tablename__ = "strava_credentials"

    id: Mapped[int] = mapped_column(primary_key=True)
    access_token: Mapped[str] = mapped_column(String, nullable=False)
    refresh_token: Mapped[str] = mapped_column(String, nullable=False)
    
    expires_at: Mapped[int] = mapped_column(BigInteger, nullable=False) 
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=func.now(), 
        onupdate=func.now()
    )    
    
class RawStravaActivity(Base):
    __tablename__ = "activities"
    __table_args__ = {"schema": "raw"} 

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    streams: Mapped[dict] = mapped_column(JSONB, nullable=True) 
    zones: Mapped[list] = mapped_column(JSONB, nullable=True)   
    
    synced_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())