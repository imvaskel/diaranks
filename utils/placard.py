import discord
from utils import Levelling
from jishaku.functools import executor_function
from disrank.generator import Generator
from .bot import Bot

@executor_function
def generate_placard(member: discord.Member, xp: int, bot: Bot, *, bg: str = '') -> discord.File:

    level = Levelling.get_level_from_xp(xp)
    remaining_xp = Levelling.get_remaining_xp(xp)

    args = {
        'bg_image': bg,
        'profile_image': str(member.avatar_url_as(format='png')),
        'level': level,
        'current_xp': 0,
        'user_xp': remaining_xp,
        'next_xp': Levelling.get_level_xp(level+1),
        'user_position': bot.get_user_position(member.id),
        'user_name': str(member),
        'user_status': member.status.name,
    }

    fp = Generator().generate_profile(**args)

    return discord.File(fp=fp, filename=f"{member.id}-rank.png")