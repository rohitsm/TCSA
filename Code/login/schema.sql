create table Login_1(
	email VARCHAR(120) NOT NULL UNIQUE PRIMARY KEY,
	-- Hashed password
	password VARCHAR(100) NOT NULL
);

create table Login_2(
	email VARCHAR(120) NOT NULL UNIQUE PRIMARY KEY, 
	-- Hashed passphrase
	passphrase VARCHAR(100) NOT NULL,
	FOREIGN KEY (email) REFERENCES Login_1(email)
);
