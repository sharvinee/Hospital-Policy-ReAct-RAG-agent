def get_value(item, name, default=None):
    """Read a field from a dictionary or object."""
    if isinstance(item, dict):
        return item.get(name, default)
    return getattr(item, name, default)
