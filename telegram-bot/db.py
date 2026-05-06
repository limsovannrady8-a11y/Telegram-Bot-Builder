from __future__ import annotations

import asyncio
import logging
import os
import re

import asyncpg

logger = logging.getLogger(__name__)

_pool: asyncpg.Pool | None = None


def _clean_dsn(url: str) -> str:
    url = re.sub(r'[&?]channel_binding=[^&]*', '', url)
    url = re.sub(r'\?&', '?', url)
    url = url.rstrip('?&')
    return url


async def init_db() -> None:
    global _pool
    raw_url = os.environ.get("NEON_DATABASE_URL", "")
    if not raw_url:
        logger.error("NEON_DATABASE_URL not set — voice cache disabled")
        return
    dsn = _clean_dsn(raw_url)
    try:
        _pool = await asyncpg.create_pool(dsn, min_size=1, max_size=5, command_timeout=15)
        async with _pool.acquire() as conn:
            # Check if table exists with correct schema; recreate if not
            col_exists = await conn.fetchval("""
                SELECT COUNT(*) FROM information_schema.columns
                WHERE table_name = 'voice_cache' AND column_name = 'audio'
            """)
            if not col_exists:
                logger.info("Recreating voice_cache table with correct schema")
                await conn.execute("DROP TABLE IF EXISTS voice_cache")
                await conn.execute("""
                    CREATE TABLE voice_cache (
                        voice_id   TEXT PRIMARY KEY,
                        audio      BYTEA NOT NULL,
                        created_at TIMESTAMPTZ DEFAULT NOW()
                    )
                """)
            else:
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS voice_cache (
                        voice_id   TEXT PRIMARY KEY,
                        audio      BYTEA NOT NULL,
                        created_at TIMESTAMPTZ DEFAULT NOW()
                    )
                """)
        logger.info("Voice cache DB ready")
    except Exception as exc:
        logger.error("DB init failed: %s", exc)
        _pool = None


async def get_cached_voice(voice_id: str) -> bytes | None:
    if _pool is None:
        return None
    try:
        async with _pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT audio FROM voice_cache WHERE voice_id = $1", voice_id
            )
            return bytes(row["audio"]) if row else None
    except Exception as exc:
        logger.warning("DB get error %s: %s", voice_id, exc)
        return None


async def save_cached_voice(voice_id: str, audio_bytes: bytes) -> None:
    if _pool is None:
        return
    try:
        async with _pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO voice_cache (voice_id, audio)
                VALUES ($1, $2)
                ON CONFLICT (voice_id) DO UPDATE
                    SET audio = EXCLUDED.audio, created_at = NOW()
                """,
                voice_id, audio_bytes,
            )
        logger.info("Cached voice %s (%d KB)", voice_id, len(audio_bytes) // 1024)
    except Exception as exc:
        logger.warning("DB save error %s: %s", voice_id, exc)


def is_ready() -> bool:
    return _pool is not None
