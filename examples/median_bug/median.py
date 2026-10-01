def median(values: list[float]) -> float:
    """Return the median; reject empty input."""
    if not values:
        raise ValueError("values must not be empty")
    ordered = sorted(values)
    return ordered[len(ordered) // 2]
