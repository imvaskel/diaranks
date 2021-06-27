-- Schema File, this will be ran whenever the database docker container is first created.

CREATE TABLE levels(
    id BIGINT PRIMARY KEY,
    xp INT DEFAULT 0
);

CREATE TABLE roles(
    level INT PRIMARY KEY,
    id BIGINT NOT NULL
);