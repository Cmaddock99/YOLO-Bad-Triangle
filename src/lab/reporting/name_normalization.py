from __future__ import annotations


NONE_LIKE_NAMES = {"", "none", "identity"}


def normalize_name(value: object) -> str:
    return str(value or "").strip().lower()


def is_none_like(value: object) -> bool:
    return normalize_name(value) in NONE_LIKE_NAMES

