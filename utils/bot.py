import logging
import operator
import os
from typing import Dict, Union, Optional

import asyncpg
import discord
import toml
from discord.ext import commands
from discord.ext.commands.errors import ExtensionError


class Bot(commands.Bot):
    def __init__(self) -> None:
        self.config = toml.load("./config.toml")
        self.logger = logging.getLogger(__name__)

        activity = self.config["bot"]["activity"]

        if activity["type"] == "gaming":
            activity = discord.Game(name=activity["text"])
        else:
            activity = discord.Activity(
                type = getattr(discord.ActivityType, activity["type"], discord.ActivityType.watching),
                name = activity["text"]
            )

        intents = discord.Intents.default()
        intents.members = True

        super().__init__(
            **self.config.get("bot").get("config"),
            activity = activity,
            allowed_mentions=discord.AllowedMentions(**self.config["bot"]["allowed_mentions"]),
            intents=intents
        )

        self.roles: Dict[int, int] = {} # Level, Role ID
        self.xp: Dict[int, int] = {} # User ID, XP
        self.loop.run_until_complete(self._ainit())

        self._configure_env()
        self._configure_logging()
        self._load_extensions()

        self.error_color = discord.Color.red()

    async def _ainit(self) -> None:
        self.db = await asyncpg.create_pool(
            **self.config.get("bot").get("database")
        )

        rows = await self.db.fetch("SELECT * FROM levels")

        for row in rows:
            self.xp[row["id"]] = row["xp"]

        rows = await self.db.fetch("SELECT * FROM roles")

        if not rows: return

        for row in rows:
            self.roles[row["level"]] = row["id"]

    def _load_extensions(self) -> None:
        for extension in self.config["bot"]["extensions"]:
            try:
                self.load_extension(extension)
                self.logger.info(f"Loaded extension {extension}")
            except ExtensionError as e:
                self.logger.error(f"Failed to load extension {extension} \n{e}", exc_info=True)

    def _configure_logging(self) -> None:
        config = self.config["bot"]["logging"]

        logger = logging.getLogger()
        logger.setLevel(getattr(logging, config["level"], logging.INFO))
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(config["format"]))
        logger.addHandler(handler)

    def _configure_env(self) -> None:
        for key, value in self.config["env"].items():
            os.environ[key] = value

    def run(self, token=None) -> None:
        return super().run(token or self.config["bot"]["token"], bot=True, reconnect=True)

    async def on_message(self, message: discord.Message) -> None:
        if message.guild is None or message.author.bot:
            return

        return await super().on_message(message)

    def get_sorted_leaderboard(self) -> list[tuple[int, int]]:
        sorted_d = dict(sorted(self.xp.items(), key=operator.itemgetter(1), reverse=True))
        return [
            (i, self.xp[i]) for i in sorted_d
        ]

    def get_user_position(self, user: Union[int, int]) -> int:
        if isinstance(user, discord.User):
            user = user.id

        index = 0

        for i, j in enumerate(self.get_sorted_leaderboard()):
            if j[0] == user:
                index = i
                break

        return index

