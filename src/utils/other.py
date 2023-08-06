def hex_to_rgba(value):
    value = value.lstrip("#")
    length = len(value)
    return tuple(
        int(value[i : i + length // 3], 16) for i in range(0, length, length // 3)
    )
