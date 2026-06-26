import aiosqlite
from datetime import datetime, timezone
from app.core.config import settings

DATABASE_PATH = settings.database_path


async def init_db():
    async with aiosqlite.connect(DATABASE_PATH) as db: 
        await db.execute("""
            CREATE TABLE IF NOT EXISTS quotes (
                id TEXT PRIMARY KEY,
                customer_id TEXT NOT NULL,
                raw_request TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        await db.commit()


async def save_quote(quote_id: str, customer_id: str, raw_request: str) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "INSERT INTO quotes (id, customer_id, raw_request, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
            (quote_id, customer_id, raw_request, "pending", now, now),
        )
        await db.commit()
    return {"id": quote_id, "customer_id": customer_id, "raw_request": raw_request, "status": "pending", "created_at": now}


async def update_quote_status(quote_id: str, status: str):
    now = datetime.now(timezone.utc).isoformat()
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "UPDATE quotes SET status = ?, updated_at = ? WHERE id = ?",
            (status, now, quote_id),
        )
        await db.commit()


async def get_quote_meta(quote_id: str) -> dict | None:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM quotes WHERE id = ?", (quote_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def list_quotes_meta() -> list[dict]:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM quotes ORDER BY created_at DESC") as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]
