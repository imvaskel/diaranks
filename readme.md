# Diaranks
Diaranks is a ranks bot specially made for discord.gg/diabetes, though anyone can use it.
Note that it is quite hard coded, and it being open source is to allow for contributions from the discord.

## Running

The official way of running the bot is running it via docker.
To start, firstly move the file ``config-template.yaml`` to ``config.yaml``. Then, fill out a file called ``.env`` with the following contents:
```env
POSTGRES_USER=...
POSTGRES_PASSWORD=...
```
Note: You can add any additional environment variables you see fit to the file, as they will be loaded on both containers.

Then, simply run ``docker compose up``.