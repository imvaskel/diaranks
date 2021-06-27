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
        if ctx.invoked_subcommand is None:
            await ctx.send_help("levels")

    @levels_group.command(name="list")
    async def list_levels(self, ctx: Context):
        end = ""

        for level, id in self.bot.roles:
            role = ctx.guild.get_role(id)
            end += f"``**{level}**``: {role.mention} \n"

        await ctx.send(embed=discord.Embed(description=end))

    @commands.has_guild_permissions(manage_guild=True)
    @levels_group.command(name="add")
    async def add_role(self, ctx: Context, role: discord.Role, level: int):
        if self.bot.roles.get(level) == level:
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
        await self.bot.db.execute(
            "DELETE FROM roles WHERE level = $1", level
        )

        await ctx.send(embed=discord.Embed(description=f"Successfully removed the role given for level ``**{level}**``"))

def setup(bot):
    bot.add_cog(ManagementCog(bot))
