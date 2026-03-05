"""
Taxonomy Service — Deterministic topic_code matching + CRUD + seed.
Primary matching: exact topic_code. Fallback: fuzzy text for legacy data.
"""
import re
import uuid
from typing import Optional, Tuple, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.models.taxonomy import SubjectTaxonomy


# In-memory cache: { topic_code: {subject, topic, aliases} }
_code_cache: Optional[dict] = None
_entries_cache: Optional[List[SubjectTaxonomy]] = None


async def _load_cache(db: AsyncSession):
    global _code_cache, _entries_cache
    stmt = select(SubjectTaxonomy).order_by(SubjectTaxonomy.subject, SubjectTaxonomy.topic)
    _entries_cache = list((await db.execute(stmt)).scalars().all())
    _code_cache = {}
    for e in _entries_cache:
        _code_cache[e.topic_code] = {
            "subject": e.subject,
            "topic": e.topic,
            "topic_code": e.topic_code,
            "aliases": e.aliases or [],
        }


def invalidate_cache():
    global _code_cache, _entries_cache
    _code_cache = None
    _entries_cache = None


def _slugify(text: str) -> str:
    """Strip all non-alphanumeric and lowercase. 'Fundamental Rights' → 'fundamentalrights'"""
    return re.sub(r'[^a-z0-9]', '', text.lower())


async def resolve_topic_code(db: AsyncSession, topic_code: str) -> Optional[dict]:
    """Resolve a topic_code to its subject + display name. Returns None if not found."""
    if _code_cache is None:
        await _load_cache(db)
    return _code_cache.get(topic_code)


async def normalize(db: AsyncSession, raw_subject: str, raw_topic: Optional[str],
                    raw_topic_code: Optional[str] = None) -> Tuple[str, str, Optional[str]]:
    """
    Resolve tags to canonical form. Returns (subject, topic_display, topic_code).
    Resolution:
      1. If topic_code is provided and valid → use it (deterministic, 100%)
      2. Exact text match on (subject, topic)
      3. Case-insensitive text match
      4. Slug match (FundamentalRights = "Fundamental Rights")
      5. Alias scan
      6. Subject-only fallback
      7. No match → return originals, topic_code=None
    """
    if _code_cache is None:
        await _load_cache(db)

    # 1. Deterministic: topic_code match
    if raw_topic_code and raw_topic_code in _code_cache:
        entry = _code_cache[raw_topic_code]
        return entry["subject"], entry["topic"], raw_topic_code

    raw_s = (raw_subject or "").strip()
    raw_t = (raw_topic or "General").strip()
    raw_s_lower = raw_s.lower()
    raw_t_lower = raw_t.lower()
    raw_s_slug = _slugify(raw_s)
    raw_t_slug = _slugify(raw_t)

    # 2. Exact text match
    for e in _entries_cache:
        if e.subject == raw_s and e.topic == raw_t:
            return e.subject, e.topic, e.topic_code

    # 3. Case-insensitive
    for e in _entries_cache:
        if e.subject.lower() == raw_s_lower and e.topic.lower() == raw_t_lower:
            return e.subject, e.topic, e.topic_code

    # 4. Slug match
    for e in _entries_cache:
        if _slugify(e.subject) == raw_s_slug and _slugify(e.topic) == raw_t_slug:
            return e.subject, e.topic, e.topic_code

    # 5. Alias scan (case-insensitive + slug)
    for e in _entries_cache:
        aliases = e.aliases or []
        aliases_lower = [a.lower() for a in aliases]
        aliases_slugs = [_slugify(a) for a in aliases]
        if raw_t_lower in aliases_lower or raw_t_slug in aliases_slugs:
            if e.subject.lower() == raw_s_lower or _slugify(e.subject) == raw_s_slug:
                return e.subject, e.topic, e.topic_code

    # 5b. Alias scan — any subject
    for e in _entries_cache:
        aliases = e.aliases or []
        aliases_lower = [a.lower() for a in aliases]
        aliases_slugs = [_slugify(a) for a in aliases]
        if raw_t_lower in aliases_lower or raw_t_slug in aliases_slugs or \
           raw_s_lower in aliases_lower or raw_s_slug in aliases_slugs:
            return e.subject, e.topic, e.topic_code

    # 6. Subject-only fallback
    for e in _entries_cache:
        if e.subject.lower() == raw_s_lower or _slugify(e.subject) == raw_s_slug:
            return e.subject, raw_t, None

    # 7. No match
    return raw_s or "General Knowledge", raw_t or "General", None


async def get_all(db: AsyncSession) -> List[dict]:
    """Get the full taxonomy tree grouped by subject."""
    if _entries_cache is None:
        await _load_cache(db)
    subjects = {}
    for e in _entries_cache:
        if e.subject not in subjects:
            subjects[e.subject] = []
        subjects[e.subject].append({
            "id": str(e.id),
            "topic": e.topic,
            "topic_code": e.topic_code,
            "aliases": e.aliases or [],
        })
    return [{"subject": s, "topics": topics} for s, topics in subjects.items()]


async def get_all_codes_flat(db: AsyncSession) -> List[dict]:
    """Get flat list of all topic codes for dropdown."""
    if _code_cache is None:
        await _load_cache(db)
    return [{"code": code, "subject": v["subject"], "topic": v["topic"]}
            for code, v in sorted(_code_cache.items())]


async def create_entry(db: AsyncSession, subject: str, topic: str, topic_code: str,
                       aliases: List[str] = []) -> SubjectTaxonomy:
    entry = SubjectTaxonomy(
        subject=subject.strip(), topic=topic.strip(), topic_code=topic_code.strip().upper(),
        aliases=[a.strip().lower() for a in aliases if a.strip()],
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    invalidate_cache()
    return entry


async def update_entry(db: AsyncSession, entry_id: uuid.UUID, subject: Optional[str] = None,
                       topic: Optional[str] = None, topic_code: Optional[str] = None,
                       aliases: Optional[List[str]] = None) -> SubjectTaxonomy:
    entry = (await db.execute(select(SubjectTaxonomy).where(SubjectTaxonomy.id == entry_id))).scalars().first()
    if not entry:
        raise ValueError("Taxonomy entry not found")
    if subject is not None: entry.subject = subject.strip()
    if topic is not None: entry.topic = topic.strip()
    if topic_code is not None: entry.topic_code = topic_code.strip().upper()
    if aliases is not None: entry.aliases = [a.strip().lower() for a in aliases if a.strip()]
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    invalidate_cache()
    return entry


async def delete_entry(db: AsyncSession, entry_id: uuid.UUID):
    entry = (await db.execute(select(SubjectTaxonomy).where(SubjectTaxonomy.id == entry_id))).scalars().first()
    if not entry:
        raise ValueError("Taxonomy entry not found")
    await db.delete(entry)
    await db.commit()
    invalidate_cache()


async def seed_default_taxonomy(db: AsyncSession):
    """Seed the complete 239-code taxonomy. Only runs if table is empty."""
    count = (await db.execute(select(func.count(SubjectTaxonomy.id)))).scalar()
    if count > 0:
        return {"status": "already_seeded", "count": count}

    from app.services.taxonomy_data import TAXONOMY_EXPANDED as TAXONOMY

    created = 0
    for subject, topic, code, aliases in TAXONOMY:
        db.add(SubjectTaxonomy(subject=subject, topic=topic, topic_code=code, aliases=aliases))
        created += 1

    await db.commit()
    invalidate_cache()
    return {"status": "seeded", "created": created}
