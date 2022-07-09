import pathlib
import docker

from datetime import datetime

from docker.models.networks import Network
from docker.models.containers import Container

def make_backup_file_name():
    now = datetime.utcnow()

    return f"backup-{now:%m-%d-%y}.sql"

FOLDER = pathlib.Path(__file__).parent
NETWORK_NAME = f"{FOLDER.name}_default"
BACKUP_NAME = make_backup_file_name()
client = docker.from_env()

network: Network = client.networks.get(NETWORK_NAME)  # type: ignore

for container in network.containers:
    container: Container = container
    name: str = container.name # type: ignore
    if "postgres" in name and FOLDER.name in name:
        res = container.exec_run("pg_dump -U postgres -d postgres")
        with open(FOLDER / "backups" / BACKUP_NAME, "wb") as fp:
            fp.write(res.output)
        print(f"written to {BACKUP_NAME}")