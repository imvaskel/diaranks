import discord, random
from discord.ext import commands

def _get_level_xp(n):
    return 5 * (n ** 2) + 50 * n + 100


def _get_level_from_xp(xp):
    remaining_xp = int(xp)
    level = 0
    while remaining_xp >= _get_level_xp(level):
        remaining_xp -= _get_level_xp(level)
        level += 1
    return level

class ListenerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_id = 257554742371155998

    async def check_and_add_roles(self, member: discord.Member):
        level = _get_level_from_xp(self.bot.ranks[member.id])
        try:
            info = self.bot.level_roles[level]
            guild = self.bot.get_guild(self.guild_id)
            role = guild.get_role(info)
            await member.add_roles(role, reason = "Automatically done for levelling up.")
        except:
            return

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id in self.bot.blacklist or message.guild.id != 257554742371155998:
            return
        if not message.author.bot:
            self.bot.ranks[message.author.id] += random.randrange(1, 6)
            await self.check_and_add_roles(message.author)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.bot.db.execute("INSERT OR IGNORE INTO ranks(userId) VALUES(?)", (member.id,))
        cursor = await self.bot.db.execute("SELECT * FROM ranks WHERE userId = ?", (member.id,))
        row = await cursor.fetchone()

        self.bot.ranks.update({row[0]: row[1]})

def setup(bot):
    bot.add_cog(ListenerCog(bot))
