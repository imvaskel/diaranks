import pathlib
from datetime import datetime

import docker
from docker.models.containers import Container
from docker.models.networks import Network


def make_backup_file_name() -> str:
    now = datetime.now()

    return f"backup-{now:%m-%d-%y}.sql"


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
