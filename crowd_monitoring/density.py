def get_status(count: int, green_max: int, yellow_max: int) -> tuple[str, tuple[int, int, int]]:
    if count <= green_max:
        return "GREEN", (0, 255, 0)

    if count <= yellow_max:
        return "YELLOW", (0, 255, 255)

    return "RED", (0, 0, 255)
