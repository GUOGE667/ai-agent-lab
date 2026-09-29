def parse_line(line: str) -> tuple[str, str]:
    """Parse KEY=VALUE, preserving any '=' characters in VALUE."""
    key, value = line.split("=")
    return key.strip(), value.strip()
