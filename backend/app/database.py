from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from backend.app.config import settings
import ssl

def _build_db_url_and_args(raw_url: str):
    """
    Normalise the DATABASE_URL for SQLAlchemy async use:
    - sqlite:///      -> sqlite+aiosqlite:///   (connect_args: check_same_thread=False)
    - postgresql://   -> postgresql+asyncpg://  (SSL configured via connect_args)
    
    Neon URLs often contain channel_binding=require and sslmode=require which
    asyncpg does not understand as query-string params; we strip them and pass
    a proper ssl.SSLContext instead.
    """
    from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

    url = raw_url.strip()

    # --- SQLite ---
    if url.startswith("sqlite"):
        if not url.startswith("sqlite+aiosqlite"):
            url = url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
        return url, {"check_same_thread": False}

    # --- PostgreSQL ---
    if url.startswith("postgresql://") or url.startswith("postgres://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)

    # Strip params asyncpg cannot handle, collect ssl intent
    parsed = urlparse(url)
    params = parse_qs(parsed.query, keep_blank_values=True)

    needs_ssl = False
    # sslmode=require / verify-full etc. → enable SSL
    sslmode = params.pop("sslmode", [None])[0]
    if sslmode and sslmode not in ("disable", "allow", "prefer"):
        needs_ssl = True
    # channel_binding is a libpq param, asyncpg doesn't know it
    params.pop("channel_binding", None)

    clean_query = urlencode({k: v[0] for k, v in params.items()})
    clean_url = urlunparse(parsed._replace(query=clean_query))

    connect_args = {}
    if needs_ssl:
        # Create a permissive SSL context (Neon provides valid certs)
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        connect_args["ssl"] = ctx

    return clean_url, connect_args


db_url, connect_args = _build_db_url_and_args(settings.DATABASE_URL)

engine = create_async_engine(
    db_url,
    echo=False,
    connect_args=connect_args,
    pool_pre_ping=True,        # reconnect after Neon serverless cold-starts
    pool_size=5,
    max_overflow=10,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
