class Levelling:

    @staticmethod
    def get_level_xp(n):
        return 5 * (n ** 2) + 50 * n + 100

    @staticmethod
    def get_level_from_xp(xp):
        remaining_xp = int(xp)
        level = 0
        while remaining_xp >= Levelling.get_level_xp(level):
            remaining_xp -= Levelling.get_level_xp(level)
            level += 1
        return level