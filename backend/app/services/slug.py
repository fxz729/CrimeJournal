"""
Slug Service - Semantic URL Generation for Legal Cases

Provides human-readable, SEO-friendly URLs for case details.
Format: {country}/{type}/{slug_name}_{case_id}/
Example: us/criminal/people-v-smith-123456789/
"""

import re
import unicodedata
from typing import Optional, Tuple


# Court ID prefix → country mapping
COURT_COUNTRY_MAP = {
    # United States
    "ca": "us",   # Federal circuits: ca1-ca11, etc.
    "cae": "us",  # Court of Appeals for the Federal Circuit
    "dcd": "us",  # DC District
    "dca": "us",  # DC Circuit / DC Court of Appeals
    "mad": "us",  # Massachusetts District
    "ny": "us",   # New York (state and federal)
    "cal": "us",  # California Supreme Court / Courts
    "penn": "us", # Pennsylvania
    "tex": "us",  # Texas
    "fl": "us",   # Florida
    "ill": "us",  # Illinois
    # Add more as needed
}

# Keywords in court name → case type
COURT_TYPE_KEYWORDS = {
    "criminal": ["criminal", "crime", "prosecution", "indictment"],
    "civil": ["civil", "tort", "contract", "liability", "damages"],
    "family": ["family", "divorce", "custody", "child"],
    "bankruptcy": ["bankruptcy", "insolvency", "bankr.", "bk."],
    "administrative": ["administrative", "agency", "regulatory"],
}


def _normalize_case_name(name: str) -> str:
    """
    Normalize case name for use in URL slug.

    - Lowercase
    - Replace spaces and punctuation with hyphens
    - Remove accented characters
    - Collapse multiple hyphens
    - Strip leading/trailing hyphens
    """
    if not name:
        return "untitled-case"

    # Unicode normalization (NFKD) to decompose accented chars
    name = unicodedata.normalize("NFKD", name)
    # Remove combining characters (accents)
    name = "".join(c for c in name if not unicodedata.combining(c))

    # Convert to lowercase
    name = name.lower()

    # Replace common separators with hyphen
    name = re.sub(r"[\s.,;:!?()\[\]{}+=*&^%$#@|\\/<>]+", "-", name)

    # Remove characters that aren't alphanumeric or hyphen
    name = re.sub(r"[^a-z0-9\-]", "", name)

    # Collapse multiple hyphens
    name = re.sub(r"-+", "-", name)

    # Strip leading/trailing hyphens
    name = name.strip("-")

    if not name:
        return "untitled-case"

    # Limit length
    if len(name) > 80:
        name = name[:80].rstrip("-")

    return name


def _infer_case_type(court_id: str, citation: str = None) -> str:
    """
    Infer case type from court ID and citation.

    Heuristics:
    - Court suffix: 'app' = appellate, 'd'/'dist' = district
    - Court name keywords
    - Citation format
    """
    if not court_id:
        return "general"

    court_lower = court_id.lower()

    # Check court suffix patterns
    if court_lower.endswith("app") or court_lower.endswith("ap") or court_lower.endswith("coa"):
        # Court of Appeal / Appellate
        return "civil"  # Most appeals are civil matters
    if court_lower.endswith("d") or court_lower.endswith("dist") or "-d" in court_lower:
        # District court - more likely criminal
        return "criminal"
    if court_lower.endswith("supreme") or court_lower.endswith("supct"):
        return "general"

    # Check for specific court types in the court_id
    if "bankr" in court_lower or "bkr" in court_lower:
        return "bankruptcy"
    if "fam" in court_lower:
        return "family"
    if "admin" in court_lower or "agency" in court_lower:
        return "administrative"
    if "crim" in court_lower:
        return "criminal"
    if "civ" in court_lower:
        return "civil"

    # Check citation for federal indicators
    # F.2d, F.3d, F.4th = Federal Circuit (civil)
    # S.E.2d, P.2d, etc. = state appellate
    # F. Supp. = Federal District (civil)
    # F. Crim. = Federal District (criminal)
    if citation:
        cite_upper = citation.upper()
        if "F. CRIM" in cite_upper or "F. SUPP. CT." in cite_upper:
            return "criminal"
        if "F.2D" in cite_upper or "F.3D" in cite_upper or "F.4TH" in cite_upper:
            return "civil"
        if "S.E.2D" in cite_upper or "P.2D" in cite_upper or "S.W." in cite_upper:
            # State appellate - likely civil by default
            return "civil"

    # Default based on court type
    # ca1, ca2...ca11 = federal circuit = civil
    # dcd, dmd, etc. = district = criminal/civil mixed
    if court_lower.startswith("ca") and len(court_lower) <= 4:
        return "civil"
    if court_lower.startswith("dcd") or court_lower.startswith("d"):
        return "criminal"

    return "general"


def _get_country(court_id: str) -> str:
    """
    Infer country from court ID.

    CourtListener primarily covers US courts.
    """
    if not court_id:
        return "us"

    court_lower = court_id.lower()

    # Check against known patterns
    for prefix, country in COURT_COUNTRY_MAP.items():
        if court_lower.startswith(prefix):
            return country

    # Check for international court patterns
    if court_lower.startswith("ew"):
        return "de"  # Germany (europäische justiz)
    if court_lower.startswith("uk"):
        return "uk"  # United Kingdom
    if court_lower in ["can", "bc", "ontario"]:
        return "ca"  # Canada

    # Default to US (CourtListener is primarily US-focused)
    return "us"


def generate_case_slug(
    case_id: int,
    case_name: str,
    court_id: str = None,
    citation: str = None,
) -> Tuple[str, str, str]:
    """
    Generate a semantic URL slug for a case.

    Args:
        case_id: CourtListener opinion ID
        case_name: Full case name
        court_id: Court identifier (e.g., 'ca9', 'calapp')
        citation: Case citation (e.g., '89 Cal.App.4th 123')

    Returns:
        Tuple of (slug_name, country, case_type)

    Example:
        >>> generate_case_slug(
        ...     case_id=123,
        ...     case_name="People v. Smith",
        ...     court_id="calapp",
        ...     citation="89 Cal.App.4th 123"
        ... )
        ('us/criminal/people-v-smith-123', 'us', 'criminal')
    """
    country = _get_country(court_id)
    case_type = _infer_case_type(court_id, citation)
    slug_name = _normalize_case_name(case_name)

    return slug_name, country, case_type


def parse_slug(slug: str) -> Tuple[Optional[str], Optional[int]]:
    """
    Parse a semantic slug back into components.

    Args:
        slug: URL slug (e.g., 'us/criminal/people-v-smith-123456789/')

    Returns:
        Tuple of (slug_name, case_id) or (None, None) if invalid

    Note:
        This extracts the slug_name and case_id but cannot recover
        the original case data. Use /api/cases/by-slug/{slug} for
        full case details.
    """
    if not slug:
        return None, None

    # Remove leading/trailing slashes
    slug = slug.strip("/")

    if not slug:
        return None, None

    # Split into parts
    parts = slug.split("/")

    if len(parts) < 1:
        return None, None

    # Last part contains slug_name_caseid
    last_part = parts[-1]

    # Find the case_id at the end (numeric segment after the LAST hyphen)
    # Pattern: any-hyphen followed by digits at the very end
    match = re.search(r"-(\d+)$", last_part)
    if match:
        case_id = int(match.group(1))
        slug_name = last_part[: match.start()]
        return slug_name, case_id

    # No case_id found
    return last_part, None


def build_slug_url(
    case_id: int,
    case_name: str,
    court_id: str = None,
    citation: str = None,
) -> str:
    """
    Build a complete semantic URL for a case.

    Args:
        case_id: CourtListener opinion ID
        case_name: Full case name
        court_id: Court identifier
        citation: Case citation

    Returns:
        Complete URL path (e.g., '/cases/us/criminal/people-v-smith-123456789/')
    """
    slug_name, country, case_type = generate_case_slug(
        case_id=case_id,
        case_name=case_name,
        court_id=court_id,
        citation=citation,
    )
    return f"/cases/{country}/{case_type}/{slug_name}-{case_id}/"
