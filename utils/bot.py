import logging
import operator
import pathlib
from datetime import datetime
from typing import TYPE_CHECKING

import discord
import yaml
from discord.ext import commands
from discord.ext.commands.errors import ExtensionError

if TYPE_CHECKING:
    import asyncpg

    from .config import Config


class Bot(commands.Bot):
    if TYPE_CHECKING:
        owner_ids: list[int]
        db: asyncpg.Pool[asyncpg.Record]

    def __init__(self) -> None:
        with pathlib.Path("./config.yaml").open() as fs:
            self.config: Config = yaml.load(fs, Loader=yaml.Loader)

        self.logger = logging.getLogger(__name__)
        self.start_time = datetime.now()

        activity = self.config["bot"]["activity"]

        if activity["type"] == "gaming":
            activity = discord.Game(name=activity["text"])
        else:
            activity = discord.Activity(
                type=getattr(
                    discord.ActivityType,
                    activity["type"],
                    discord.ActivityType.watching,
                ),
                name=activity["text"],
            )

        super().__init__(
            **self.config.get("bot").get("config"),
            activity=activity,
            allowed_mentions=discord.AllowedMentions.none(),
            intents=discord.Intents.all(),
        )

        self.roles: dict[int, int] = {}  # Level, Role ID
        self.xp: dict[int, int] = {}  # User ID, XP
        self.blacklist: list[int] = []  # list of blacklisted channel ids

        self._configure_logging()

        self.error_color = discord.Color.red()

    async def fetch_rows(self) -> None:
        levels = await self.db.fetch("SELECT * FROM levels")
        for row in levels:
            self.xp[row["id"]] = row["xp"]

        roles = await self.db.fetch("SELECT * FROM roles")
        for row in roles:
            self.roles[row["level"]] = row["id"]

        blacklist = await self.db.fetch("SELECT * FROM blacklist")
        for row in blacklist:
            self.blacklist.append(row["id"])

    async def _load_extensions(self) -> None:
        for extension in self.config["bot"]["extensions"]:
            try:
                await self.load_extension(extension)
                self.logger.info("Loaded extension %s", extension)
            except ExtensionError:
                self.logger.exception("Failed to load extension %s \n", extension)

    async def setup_hook(self) -> None:
        await self.fetch_rows()
        await self._load_extensions()

    def _configure_logging(self) -> None:
        config = self.config["bot"]["logging"]

        logger = logging.getLogger()
        logger.setLevel(getattr(logging, config["level"], logging.INFO))
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(config["format"]))
        logger.addHandler(handler)

    def run(self, token: str | None = None) -> None:
        return super().run(token or self.config["bot"]["token"])

    async def start(self, token: str | None = None) -> None:
        return await super().start(token or self.config["bot"]["token"])

    async def on_message(self, message: discord.Message) -> None:
        if message.guild is None or message.author.bot:
            return

        return await super().on_message(message)

    def get_sorted_leaderboard(self) -> list[tuple[int, int]]:
        return sorted(self.xp.items(), key=operator.itemgetter(1), reverse=True)

    def get_user_position(self, user: int | discord.User) -> int:
        if isinstance(user, discord.User):
            user = user.id

        leaderboard = self.get_sorted_leaderboard()

        for index, entry in enumerate(leaderboard, start=1):
            if entry[0] == user:
                return index
        else:
            return 0
