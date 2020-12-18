import discord
from discord.ext import commands
from discord.ext.commands import Cog

class ModeratorCog(Cog, name = "Moderator"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_guild = True)
    async def blacklist(self, ctx, channel: discord.TextChannel):
        """Blacklists a channel from giving xp"""
        if channel.id in self.bot.blacklist: return await ctx.send("Seems that that channel is already blacklisted")

        await self.bot.db.execute("INSERT INTO blacklist(channelId) VALUES(?)", (channel.id,))

        self.bot.blacklist.append(channel.id)

        await ctx.send(f"{channel.mention} successfully blacklisted.")

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def unblacklist(self, ctx, channel: discord.TextChannel):
        """Unblacklists a channel from giving xp"""
        if channel.id not in self.bot.blacklist: return await ctx.send("Seems that that channel is not blacklisted.")

        await self.bot.db.execute("DELETE FROM blacklist WHERE channelId = ?", (channel.id,))

        self.bot.blacklist.remove(channel.id)

        await ctx.send(f"{channel.mention} successfully unblacklisted.")

    @commands.group(name = "levels")
    async def level_group(self, ctx):
        """A group of commands that deals with level up roles."""
        if ctx.invoked_subcommand is None:
            await ctx.send(f"No subcommand passed, use `{ctx.prefix}help levels` to see the commands.")

    @level_group.command(name = "add")
    @commands.has_permissions(manage_guild = True)
    async def add_level_role(self, ctx, level: int, *, role: discord.Role):
        """Adds autorole to the given level"""
        try:
            self.bot.level_roles[level]
            return await ctx.send("Seems this role is already bound to a level.")
        except:
            pass

        await self.bot.db.execute("INSERT INTO roles(roleId, level) VALUES(?, ?)", (role.id, level))

        self.bot.level_roles.update({level: role.id})

        await ctx.reply(embed = discord.Embed(description=f"Successfully added {role.mention} to be given at level {level}"))

    @level_group.command(name = "remove")
    @commands.has_permissions(manage_guild=True)
    async def remove_level_role(self, ctx, level: int):
        """Removes autorole to the given level"""
        try:
            self.bot.level_roles[level]
        except:
            return await ctx.reply("This level has no role bound to it.")

        await self.bot.db.execute("DELETE FROM roles WHERE level = ?", (level,))

        del self.bot.level_roles[level]

        await ctx.reply(
            embed=discord.Embed(description=f"Successfully removed autorole from level {level}"))

    @level_group.command(name = "list")
    async def list_level_roles(self, ctx):
        roles = [[level, ctx.guild.get_role(self.bot.level_roles[level])] for level in self.bot.level_roles.keys()]
        s = ""

        for entry in roles:
            s += f"`{entry[0]}`:    {entry[1].mention}\n"

        await ctx.reply(embed = discord.Embed(title = "Level:   Role", description=s, color = self.bot.embed_color))


def setup(bot):
    bot.add_cog(ModeratorCog(bot))