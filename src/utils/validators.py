"""Input validation utilities."""


def parse_seed(s: str) -> int | None:
    """
    Parse seed input from user.
    
    Args:
        s: Seed string from input field
        
    Returns:
        Integer seed or None for random
    """
    t = (s or "").strip()
    if t == "" or t.lower() == "none":
        return None
    try:
        return int(t)
    except ValueError:
        return None
