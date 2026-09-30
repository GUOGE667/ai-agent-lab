def page(items: list, page_number: int, page_size: int) -> list:
    """Return a one-based page of items."""
    start = page_number * page_size
    return items[start:start + page_size]
