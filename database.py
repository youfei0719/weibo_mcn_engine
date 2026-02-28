import os
from datetime import date
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy import String, Integer, BigInteger, Date, Text, Float
from sqlalchemy.dialects.postgresql import insert

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "password")
DB_NAME = os.getenv("DB_NAME", "weibo_mcn")
DB_PORT = os.getenv("DB_PORT", "5432")

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_async_engine(DATABASE_URL, echo=False, pool_size=10, max_overflow=20)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

class Account(Base):
    __tablename__ = "accounts"
    uid: Mapped[str] = mapped_column(String(50), primary_key=True, comment="微博UID")
    nickname: Mapped[str] = mapped_column(String(100), nullable=False)
    avatar: Mapped[str] = mapped_column(Text, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    gender: Mapped[str] = mapped_column(String(10), nullable=True)
    location: Mapped[str] = mapped_column(String(100), nullable=True)
    verified_reason: Mapped[str] = mapped_column(Text, nullable=True)

class AccountDailyStat(Base):
    __tablename__ = "account_daily_stats"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    uid: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    record_date: Mapped[date] = mapped_column(Date, default=date.today)
    followers_count: Mapped[int] = mapped_column(BigInteger, default=0)
    friends_count: Mapped[int] = mapped_column(BigInteger, default=0)
    statuses_count: Mapped[int] = mapped_column(BigInteger, default=0)

class AccountCommercialStat(Base):
    __tablename__ = "account_commercial_stats"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    uid: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    record_date: Mapped[date] = mapped_column(Date, default=date.today)
    cpm: Mapped[float] = mapped_column(Float, default=0.0)
    original_price: Mapped[float] = mapped_column(Float, default=0.0)
    repost_price: Mapped[float] = mapped_column(Float, default=0.0)
    expected_reads: Mapped[int] = mapped_column(Integer, default=0)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)