def reserve(stock: dict[str, int], request: dict[str, int]) -> dict[str, int]:
    """Return new stock after a valid reservation; leave input unchanged."""
    updated = stock.copy()
    for sku, quantity in request.items():
        updated[sku] = updated.get(sku, 0) - quantity
        if quantity < 0 or updated[sku] < 0:
            raise ValueError("invalid reservation")
    return updated
