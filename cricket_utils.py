"""Shared defensive helpers for cricket API services."""
from __future__ import annotations

from typing import Any, Mapping

DEFAULT_TEAM_NAME = "TBD"
UNKNOWN_PLAYER_NAME = "Unknown"

EXTRA_SCORE_FIELDS = {
    "wide": "wides",
    "no_ball": "no_balls",
    "bye": "byes",
    "leg_bye": "leg_byes",
    "penalty": "penalties",
}
ILLEGAL_EXTRA_TYPES = frozenset(("wide", "no_ball"))
EXTRA_TYPES = frozenset(EXTRA_SCORE_FIELDS)
TOTAL_EXTRAS_FIELD = "total_extras"


def safe_int(value: Any, default: int = 0, *, minimum: int = 0) -> int:
    """Return a bounded int for partially trusted in-memory data."""
    if value is None or isinstance(value, bool):
        return default
    try:
        number = int(value)
    except (TypeError, ValueError):
        return default
    return max(minimum, number)


def safe_float(value: Any, default: float = 0.0, *, minimum: float = 0.0) -> float:
    if value is None or isinstance(value, bool):
        return default
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return max(minimum, number)


def safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text or default


def safe_extra_type(row: Mapping[str, Any]) -> str | None:
    extra_type = safe_str(row.get("extra_type")).lower()
    return extra_type if extra_type in EXTRA_TYPES else None


def is_legal_delivery(row: Mapping[str, Any]) -> bool:
    return safe_extra_type(row) not in ILLEGAL_EXTRA_TYPES


def is_wicket(row: Mapping[str, Any]) -> bool:
    return bool(row.get("is_wicket", False))


def player_name(row: Mapping[str, Any], fallback: str) -> str:
    return safe_str(row.get("player_name"), fallback)
