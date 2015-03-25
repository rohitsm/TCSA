-- CREATE DATABASE IF NOT EXISTS users;

USE users;

CREATE TABLE Login(
	email VARCHAR(120) NOT NULL PRIMARY KEY,
	-- Hashed password
	password VARCHAR(100) NOT NULL,
	-- One Time Password Key
	otp_key VARCHAR(100) NOT NULL,
	-- Public key
	pub_key BLOB NOT NULL
) ENGINE=InnoDB;


CREATE TABLE Profile(
	email VARCHAR(120) NOT NULL PRIMARY KEY,
	
	-- Columns for access_tokens
	dropbox BLOB,
	gdrive BLOB,
	
	FOREIGN KEY email(email) REFERENCES Login(email)
	ON UPDATE CASCADE
	ON DELETE CASCADE
)ENGINE=InnoDB;