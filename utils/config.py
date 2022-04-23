from __future__ import annotations

from typing import Any, TypedDict

__all__ = ("Config",)


class Config(TypedDict):
    ranks: RanksConfig
    bot: BotConfig


class RanksConfig(TypedDict):
    cooldown: int
    min: int
    max: int
    id: int


class BotConfig(TypedDict):
    token: str
    id: int
    extensions: list[str]
    config: dict[str, Any]
    activity: ActivityConfig
    logging: LoggingConfig
    database: DatabaseConfig


class ActivityConfig(TypedDict):
    type: str
    text: str


class LoggingConfig(TypedDict):
    level: str
    format: str


class DatabaseConfig(TypedDict):
    host: str
    port: int
    user: str
    password: str
