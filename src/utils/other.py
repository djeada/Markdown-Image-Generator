def hex_to_rgba(hex_value: str):
    """
    Convert a hex color code to an RGBA tuple.

    Args:
        hex_value (str): The hex color code starting with "#" and followed by 3, 4, 6, or 8 hexadecimal characters.

    Returns:
        tuple: A tuple representing the RGBA color. Each element is an integer from 0 to 255.

    Raises:
        ValueError: If the input is not a valid hex color code.
    """
    hex_value = hex_value.lstrip("#")
    if len(hex_value) not in [3, 4, 6, 8]:
        raise ValueError("Invalid hex color code")

    if len(hex_value) in [3, 4]:  # Short form like #RGB or #RGBA
        hex_value = "".join([c * 2 for c in hex_value])

    return tuple(int(hex_value[i : i + 2], 16) for i in range(0, len(hex_value), 2))
