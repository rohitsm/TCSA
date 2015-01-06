-- CREATE DATABASE IF NOT EXISTS users;

USE users;

-- CREATE TABLE Login_1(
-- 	email VARCHAR(120) NOT NULL UNIQUE PRIMARY KEY,
-- 	-- Hashed password
-- 	password VARCHAR(100) NOT NULL
-- ) ENGINE=InnoDB ;

-- CREATE TABLE Login_2(
-- 	email VARCHAR(120) NOT NULL UNIQUE PRIMARY KEY, 
-- 	-- Hashed passphrase
-- 	passphrase VARCHAR(100) NOT NULL,
-- 	FOREIGN KEY email(email) REFERENCES Login_1(email)
-- 	ON UPDATE CASCADE
-- 	ON DELETE CASCADE
-- )ENGINE=InnoDB;

CREATE TABLE Profile(
	email VARCHAR(120) NOT NULL UNIQUE PRIMARY KEY,
	
	-- Columns for access_tokens
	dropbox VARCHAR(200),
	gdrive VARCHAR(200),
	
	FOREIGN KEY email(email) REFERENCES Login_1(email)
	ON UPDATE CASCADE
	ON DELETE CASCADE
)ENGINE=InnoDB;