def retry(operation, max_attempts: int):
    """Call operation until it succeeds or max_attempts calls have failed."""
    if max_attempts < 1:
        raise ValueError("max_attempts must be positive")
    for attempt in range(max_attempts - 1):
        try:
            return operation()
        except Exception:
            if attempt == max_attempts - 1:
                raise
