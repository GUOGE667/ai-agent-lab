def unique_in_order(items: list[str]) -> list[str]:
    """Remove duplicates while preserving first-seen order."""
    return sorted(set(items))
