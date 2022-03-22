from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import discord
from discord.ext import commands, menus
from discord.ext.commands.context import Context

if TYPE_CHECKING:
    from utils import Bot

class ManagementCog(commands.Cog, name="Management"):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.group(name="levels")
    async def levels_group(self, ctx: Context):
        """
        The base group for setting up level rewards.
        """
        if ctx.invoked_subcommand is None:
            await ctx.send_help("levels")

    @levels_group.command(name="list")
    async def list_levels(self, ctx: Context):
        """
        Lists the currently active roles with their levels.
        """
        end = ""

        for level, id in self.bot.roles.items():
            role = ctx.guild.get_role(id)
            end += f"``{level}``: {role.mention} \n"

        await ctx.send(embed=discord.Embed(description=end))

    @commands.has_guild_permissions(manage_guild=True)
    @levels_group.command(name="add")
    async def add_role(self, ctx: Context, role: discord.Role, level: int):
        """
        Add a role bound to a level
        You cannot have multiple roles bound to a single level.
        """
        if level in self.bot.roles.keys():
            raise commands.BadArgument("Level cannot already have a role, please use `levels remove <level>` to remove it and try again.")

        row = await self.bot.db.fetchone((
                "INSERT INTO roles(level, id) VALUES($1, $2)"
                "RETURNING *"
            ), level, role.id
        )

        self.bot.roles[row["level"]] = row["id"]

        await ctx.reply(embed=discord.Embed(description=f"Successfully set level `**{level}**` to give role {role.mention}."))

    @commands.has_guild_permissions(manage_guild=True)
    @levels_group.command(name="remove")
    async def remove_role(self, ctx: Context, level: int):
        """
        Removes a role from the role rewards.
        """
        if level not in self.bot.roles.keys():
            raise commands.BadArgument("That level has no role bound to it.")

        await self.bot.db.execute(
            "DELETE FROM roles WHERE level = $1", level
        )

        self.bot.roles.pop(level, None)

        await ctx.send(embed=discord.Embed(description=f"Successfully removed the role given for level ``**{level}**``"))

    @commands.has_guild_permissions(manage_guild=True)
    @commands.group(name="blacklist")
    async def blacklist_group(self, ctx: commands.Context):
        """
        Base group for the blacklist command.
        """
        if ctx.invoked_subcommand is None:
            await ctx.send_help("blacklist")

    @commands.has_guild_permissions(manage_guild=True)
    @blacklist_group.command(name="add")
    async def add_channel(self, ctx: commands.Context, *, channel: discord.TextChannel):
        """
        Add a channel to the blacklist.
        """
        if channel.id in self.bot.blacklist:
            raise commands.BadArgument("This channel is already blacklisted.")

        async with self.bot.db.acquire() as conn:
            await conn.execute(
                "INSERT INTO blacklist(id) VALUES($1) RETURNING *", channel.id
            )

            self.bot.blacklist.append(channel.id)

        await ctx.message.add_reaction("\U00002705")

    @commands.has_guild_permissions(manage_guild=True)
    @blacklist_group.command(name="remove")
    async def remove_channel(self, ctx: commands.Context, *, channel: discord.TextChannel):
        """
        Remove a channel from the blacklist.
        """
        if channel.id not in self.bot.blacklist:
            raise commands.BadArgument("This channel is not blacklisted.")

        async with self.bot.db.acquire() as conn:
            await conn.execute(
                "DELETE FROM blacklist WHERE id = $1", channel.id
            )

            self.bot.blacklist.remove(channel.id)
        
        await ctx.message.add_reaction("\U00002705")

    @blacklist_group.command(name="list")
    async def list_channels(self, ctx: commands.Context):
        """
        List blacklisted channels
        """
        await ctx.send(embed=discord.Embed(description="\n".join(f"``{ctx.guild.get_channel(channel)}``" for channel in self.bot.blacklist) or "None"))

async def setup(bot):
    await bot.add_cog(ManagementCog(bot))
