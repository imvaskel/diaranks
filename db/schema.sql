-- Schema File, this will be ran whenever the database docker container is first created.

CREATE TABLE levels(
    id BIGINT PRIMARY KEY,
    xp INT DEFAULT 0
);

CREATE TABLE roles(
    level BIGINT PRIMARY KEY,
    id BIGINT NOT NULL
);

CREATE TABLE blacklist(
    id BIGINT PRIMARY KEY
);