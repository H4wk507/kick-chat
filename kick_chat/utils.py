def hex_to_rgb(val: str) -> tuple[int, int, int]:
    return (int(val[i : i + 2], 16) for i in (1, 3, 5))
