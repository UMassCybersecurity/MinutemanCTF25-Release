CREATE DATABASE IF NOT EXISTS cartoons_db;
USE cartoons_db;

CREATE TABLE IF NOT EXISTS cartoons (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    release_year INT,
    characters TEXT
);

INSERT INTO cartoons (name, release_year, characters) VALUES
("SpongeBob SquarePants", 1999, "SpongeBob, Patrick, Squidward"),
("Avatar: The Last Airbender", 2005, "Aang, Katara, Sokka, Zuko"),
("Tom and Jerry", 1940, "Tom, Jerry"),
("The Simpsons", 1989, "Homer, Marge, Bart, Lisa, Maggie");

CREATE TABLE IF NOT EXISTS flag (
    id INT AUTO_INCREMENT PRIMARY KEY,
    flag VARCHAR(255) NOT NULL
);

INSERT INTO flag (flag) VALUES ("MINUTEMAN{s3Qu3l1_1nJ3c710n_15_4w350m3}");

GRANT SELECT ON cartoons_db.* TO 'cartoon_user'@'%';
FLUSH PRIVILEGES;