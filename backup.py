import datetime
import pathlib
import re
from datetime import date

import docker
from docker.models.containers import Container
from docker.models.networks import Network


def make_backup_file_name(date: datetime.date = date.today()) -> str:
    return f"backup-{date:%m-%d-%y}.sql"


NAME_REGEX = re.compile(r"backup-(?P<month>\d+)-(?P<day>\d+)-(?P<year>\d+).sql")
FOLDER = pathlib.Path(__file__).parent
NETWORK_NAME = f"{FOLDER.name}_default"
BACKUP_NAME = make_backup_file_name()
client = docker.from_env()

network: Network = client.networks.get(NETWORK_NAME)  # type: ignore

for container in network.containers:
    container: Container = container
    name: str = container.name  # type: ignore
    if "postgres" in name and FOLDER.name in name:
        res = container.exec_run("pg_dump -U postgres -d postgres")
        with pathlib.Path(FOLDER / "backups" / BACKUP_NAME).open("wb") as fp:
            fp.write(res.output)
        print(f"written to {BACKUP_NAME}")

today = date.today()
last_week = date.today() - datetime.timedelta(days=7)

print(f"discarding backups older than {last_week:%m-%d-%y}.")

for file in pathlib.Path("backups/").iterdir():
    if match := NAME_REGEX.match(file.name):
        day = int(match["day"])
        month = int(match["month"])
        year = int(match["year"]) + 2000
        d = date(year, month, day)
        if not last_week <= d <= today:
            print(f"deleting {file.name}")
            file.unlink()
