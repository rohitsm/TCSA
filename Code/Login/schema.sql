create table login1(
	email VARCHAR(120) NOT NULL UNIQUE PRIMARY KEY,
	-- Hashed password
	password VARCHAR(100) NOT NULL,
);

create table login2(
	email VARCHAR(120) NOT NULL UNIQUE PRIMARY KEY,
	-- Hashed passphrase
	passphrase VARCHAR(100) NOT NULL,
);
