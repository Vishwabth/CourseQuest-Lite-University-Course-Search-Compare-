from fastapi import APIRouter, Header, HTTPException
from ..settings import settings
from ..cache import clear_cache_prefix
from typing import Optional
router = APIRouter(prefix="/api")

@router.post("/cache/clear")
def clear_cache(
    prefix: Optional[str] = None,
    x_admin_token: Optional[str] = Header(default=None),
):
    """Clear Redis or in-memory cache. 
    - If `prefix` is given, clears only keys with that prefix.
    - Otherwise clears common prefixes (courses, meta, ask, compare)."""

    if x_admin_token != settings.INGEST_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if prefix:
        cleared = clear_cache_prefix(prefix)
        return {"status": "ok", "cleared": prefix, "keys": cleared}

    cleared_all = []
    for p in ["courses:", "meta", "ask:", "compare:"]:
        cleared_all.append({p: clear_cache_prefix(p)})
    return {"status": "ok", "cleared": cleared_all}
