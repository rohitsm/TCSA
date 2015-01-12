-- CREATE DATABASE IF NOT EXISTS users;

USE users;

CREATE TABLE Login(
	email VARCHAR(120) NOT NULL UNIQUE PRIMARY KEY,
	-- Hashed password
	password VARCHAR(100) NOT NULL,
	-- Hashed passphrase
	passphrase VARCHAR(100) NOT NULL
) ENGINE=InnoDB;

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
	dropbox BLOB,
	gdrive BLOB,
	
	FOREIGN KEY email(email) REFERENCES Login(email)
	ON UPDATE CASCADE
	ON DELETE CASCADE
)ENGINE=InnoDB;