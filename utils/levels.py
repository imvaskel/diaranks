def get_level_xp(n):
    return 5 * (n ** 2) + 50 * n + 100


def get_remaining_xp(xp):
    remaining_xp = int(xp)
    level = 0
    while remaining_xp >= get_level_xp(level):
        remaining_xp -= get_level_xp(level)
        level += 1
    return remaining_xp


def get_xp_for_level(level):
    xp = 0
    for i in range(level + 1):
        xp += get_level_xp(i)
    return xp


def get_level_from_xp(xp):
    remaining_xp = int(xp)
    level = 0
    while remaining_xp >= get_level_xp(level):
        remaining_xp -= get_level_xp(level)
        level += 1
    return level
