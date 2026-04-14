import hashlib
import json
import logger

# ── Pattern 1: Cache-Aside ──
# Most common pattern
# Application manages cache manually

async def get_user(user_id: int, db, cache) -> dict:
    cache_key = f"user:{user_id}"

    # 1. Check cache first
    cached = await cache.get(cache_key)
    if cached:
        logger.info("cache_hit", key=cache_key)
        return cached

    # 2. Cache miss — query database
    logger.info("cache_miss", key=cache_key)
    user = await db.get(User, user_id)
    if not user:
        return None

    user_dict = {
        "id":    user.id,
        "email": user.email,
        "role":  user.role
    }

    # 3. Store in cache for 5 minutes
    await cache.set(cache_key, user_dict, ttl=300)

    return user_dict


# Invalidate when user changes
async def update_user(user_id: int, data: dict, db, cache):
    user = await db.get(User, user_id)
    for key, value in data.items():
        setattr(user, key, value)
    await db.commit()

    # Invalidate cache so next read gets fresh data
    await cache.delete(f"user:{user_id}")


# ── Pattern 2: RAG Response Cache ──

def make_rag_cache_key(query: str, doc_ids: list[int]) -> str:
    """
    Unique cache key from query + document set.
    Same query on different docs = different cache entry.
    """
    normalized = query.lower().strip()
    doc_str    = ",".join(str(id) for id in sorted(doc_ids))
    raw        = f"{normalized}|{doc_str}"
    return f"rag:{hashlib.md5(raw.encode()).hexdigest()}"


async def cached_rag_query(
    query:   str,
    doc_ids: list[int],
    pipeline,
    cache,
    ttl: int = 300
) -> dict:
    cache_key = make_rag_cache_key(query, doc_ids)

    # Check cache
    cached = await cache.get(cache_key)
    if cached:
        cached['from_cache'] = True
        return cached

    # Run RAG pipeline
    result = await pipeline.query(query, doc_ids)

    # Cache the result
    await cache.set(cache_key, result, ttl=ttl)

    result['from_cache'] = False
    return result


# ── Pattern 3: Rate Limiting ──

async def check_rate_limit(
    user_id:       int,
    limit:         int = 10,
    window_secs:   int = 60,
    cache         = cache
) -> tuple[bool, int]:
    """
    Limit user to N requests per time window.
    Returns (is_allowed, current_count)
    """
    key     = f"rate_limit:{user_id}:{window_secs}"
    count   = await cache.increment(key, ttl=window_secs)
    allowed = count <= limit

    if not allowed:
        logger.warning(
            "rate_limit_exceeded",
            user_id=user_id,
            count=count,
            limit=limit
        )

    return allowed, count



# ── Pattern 4: Semantic Cache ──
# Cache by MEANING not exact text

async def semantic_cache_get(
    query:     str,
    cache,
    vectorstore,
    threshold: float = 0.95
) -> Optional[str]:
    """
    Find cached answer for semantically similar query.
    "What is max loan?" matches "Maximum loan amount?"
    """
    query_embedding = await embed(query)

    # Find similar cached queries in vector store
    similar = await vectorstore.similarity_search_with_score(
        query,
        k=1,
        filter={"is_cached": True}
    )

    if similar and similar[0][1] >= threshold:
        cached_key = similar[0][0].metadata['cache_key']
        return await cache.get(f"semantic:{cached_key}")

    return None


async def semantic_cache_set(
    query:  str,
    answer: str,
    cache,
    vectorstore,
    ttl: int = 3600
):
    """Store query embedding for future similarity lookup"""
    cache_key = hashlib.md5(query.encode()).hexdigest()

    # Store answer in Redis
    await cache.set(f"semantic:{cache_key}", answer, ttl=ttl)

    # Store embedding in vector store for lookup
    await vectorstore.aadd_texts(
        texts=[query],
        metadatas=[{
            "is_cached": True,
            "cache_key": cache_key
        }]
    )