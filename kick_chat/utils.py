def hex_to_rgb(val: str) -> tuple[int, int, int]:
    return (int(val[1:3], 16), int(val[3:5], 16), int(val[5:7], 16))
