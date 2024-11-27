DROP TABLE IF EXISTS product;
DROP TABLE IF EXISTS client;
DROP TABLE IF EXISTS orders;


CREATE TABLE product (
	id INTEGER PRIMARY KEY NOT NULL,
	name TEXT NOT NULL UNIQUE,
	manufacturer TEXT NOT NULL,
	weight INTEGER NOT NULL,
	price INTEGER NOT NULL,
	quantity INTEGER NOT NULL DEFAULT 0,
	photo_url TEXT NOT NULL);

CREATE TABLE client (
	id INTEGER PRIMARY KEY NOT NULL,
	company_name TEXT NOT NULL UNIQUE,
	address TEXT NOT NULL,
	contact_number INTEGER NOT NULL UNIQUE);

CREATE TABLE orders (
	id INTEGER PRIMARY KEY NOT NULL,
	product_id INTEGER NOT NULL,
	client_id INTEGER NOT NULL,
	quantity INTEGER NOT NULL,
	status TEXT NOT NULL DEFAULT "Заказ оформлен",
	FOREIGN KEY(product_id) REFERENCES product(id) ON DELETE NO ACTION ON UPDATE NO ACTION,
	FOREIGN KEY(client_id) REFERENCES client(id) ON DELETE NO ACTION ON UPDATE NO ACTION);