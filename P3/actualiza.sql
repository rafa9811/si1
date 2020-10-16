------------------------------------------------------------------------
-- ACTUALIZA SQL --
--
-- Autores:
-- 	- Rafael Hidalgo Alejo: rafael.hidalgoa@estudiante.uam.es
--	- Carlos Molinero Alvarado: carlos.molineroa@estudiante.uam.es
------------------------------------------------------------------------

---------------------order-----------------------------
-- Establece una clave foránea para la tabla order.
ALTER TABLE orders ADD CONSTRAINT orders_fkey FOREIGN KEY (customerid) REFERENCES customers(customerid);

-- actualiza el serial por una posible pérdida de la secuencia.
BEGIN;
LOCK TABLE orders IN EXCLUSIVE MODE;
SELECT setval('orders_orderid_seq', COALESCE((SELECT MAX(orderid) + 1 FROM orders), 1), false);
COMMIT;


---------------------actormovies-----------------------
-- Establece la clave primaria para la tabla actormovies.
ALTER TABLE imdb_actormovies ADD CONSTRAINT actormovies_pkey PRIMARY KEY (actorid, movieid);

-- Establece las claves foráneas para la tabla actormovies.
ALTER TABLE imdb_actormovies ADD CONSTRAINT actormovies_fk1 FOREIGN KEY (actorid) REFERENCES imdb_actors(actorid);

ALTER TABLE imdb_actormovies ADD CONSTRAINT actormovies_fk2 FOREIGN KEY (movieid) REFERENCES imdb_movies(movieid);


---------------atributos multievaluados-----------------
--LENGUAJES.

--crear tabla de lenguajes.
CREATE TABLE languages (
	languageid serial CONSTRAINT pkey PRIMARY KEY,
	name varchar(32)
);

-- inserta valores en la tabla de lenguajes.
INSERT INTO languages(name)
SELECT language FROM imdb_movielanguages GROUP BY language;

-- actualizar los datos de movielanguage.
UPDATE imdb_movielanguages SET language = languages.languageid
FROM languages
WHERE languages.name = imdb_movielanguages.language;

-- modificar el tipo de dato de la columna language (son todos carac. numericos, por lo que podemos hacer un casting)
ALTER TABLE imdb_movielanguages ALTER COLUMN language SET DATA TYPE integer USING language::integer;

-- añadimos la fkey de imd_languages.
ALTER TABLE imdb_movielanguages ADD CONSTRAINT c_fkey FOREIGN KEY(language) REFERENCES languages(languageid) ON DELETE CASCADE;


--PAISES.

--crear tabla de paises.
CREATE TABLE countries (
	countryid serial CONSTRAINT p_key_countries PRIMARY KEY,
	name varchar(32)
);

-- inserta valores en la tabla nueva de countries.
INSERT INTO countries(name)
SELECT country FROM imdb_moviecountries GROUP BY country;

-- también estarán disponibles los países que se encuentren en los customers. Los añadiremos si no existen de la siguiente forma.
INSERT INTO countries(name) SELECT customers.country
FROM customers
WHERE NOT EXISTS (SELECT name FROM countries);

-- actualizar los datos de imdb_moviecountries.
UPDATE imdb_moviecountries SET country = countries.countryid
FROM countries
WHERE countries.name = imdb_moviecountries.country;

-- actualizar el tipo de dato de la columna country (ahora es un entero)
ALTER TABLE imdb_moviecountries ALTER COLUMN country SET DATA TYPE integer USING country::integer;

-- actualizar los datos de customers.
UPDATE customers SET country = countries.countryid
FROM countries
WHERE countries.name = customers.country;

-- actualizar el tipo de dato de la columna country (ahora es un entero)
ALTER TABLE customers ALTER COLUMN country SET DATA TYPE integer USING country::integer;

-- lógicamente, country deberá referenciar a su tabla.
ALTER TABLE customers ADD CONSTRAINT customers_country_fkey FOREIGN KEY(country) REFERENCES countries(countryid);

-- añadir fkey a la tabla imdb_moviecountries que referencie la tabla creada.
ALTER TABLE imdb_moviecountries ADD CONSTRAINT country_fkey FOREIGN KEY(country) REFERENCES countries(countryid) ON DELETE CASCADE;


--GÉNERO.

-- crear tabla género.
CREATE TABLE genres (
	genreid serial CONSTRAINT genre_pkey PRIMARY KEY,
	name varchar(32)
);

-- insertar los datos en la nueva tabla genre.
INSERT INTO genres(name)
SELECT genre FROM imdb_moviegenres GROUP BY genre;

-- modificamos los datos existentes en imdb_moviegenre (nombre del género por el id).
UPDATE imdb_moviegenres SET genre = genres.genreid
FROM genres
WHERE genres.name = imdb_moviegenres.genre;

-- modificar el tipo de dato de la columna genre (son todos carac. numericos, por lo que podemos hacer un casting).
ALTER TABLE imdb_moviegenres ALTER COLUMN genre SET DATA TYPE integer USING genre::integer;

-- añadir fkey a la tabla imdb_moviegenres que referencie la tabla creada.
ALTER TABLE imdb_moviegenres ADD CONSTRAINT genre_fkey FOREIGN KEY(genre) REFERENCES genres(genreid) ON DELETE CASCADE;


---------------------orderdetail ------------------------
-- nos creamos tabla auxiliar para guardar los datos definitivos.
CREATE TABLE aux AS
	SELECT orderid, prod_id, price, sum(quantity) as quantity
	FROM orderdetail
	GROUP BY orderid, prod_id, price;

-- y actualizamos.
drop table orderdetail;

ALTER TABLE aux
RENAME TO orderdetail;

ALTER TABLE orderdetail ALTER COLUMN quantity SET DATA TYPE integer USING quantity::integer;

-- Establecemos la clave primaria para orderdetail.
ALTER TABLE orderdetail ADD CONSTRAINT odet_pkey PRIMARY KEY(orderid, prod_id);


--------------------customers------------------
-- eliminamos condicion not null de los campos donde no los necesitamos.
alter table customers alter column firstname drop not null;
alter table customers alter column lastname drop not null;
alter table customers alter column address1 drop not null;
alter table customers alter column city drop not null;
alter table customers alter column country drop not null;
alter table customers alter column region drop not null;
alter table customers alter column creditcardtype drop not null;
alter table customers alter column creditcard drop not null;
alter table customers alter column creditcardexpiration drop not null;

-- actualiza el serial por una posible pérdida de la secuencia.
BEGIN;
LOCK TABLE customers IN EXCLUSIVE MODE;
select setval('customers_customerid_seq', COALESCE((SELECT MAX(customerid) + 1 FROM customers), 1), false);
COMMIT;

-- añade fkey a la tabla inventory, haciendo referencia a la de productos con prod_id.
ALTER TABLE inventory ADD CONSTRAINT inv_fkey FOREIGN KEY (prod_id) REFERENCES products (prod_id);

-- creamos una tabla auxiliar para guardar las dos columnas de stock y sales.
CREATE TABLE aux AS
SELECT * FROM PRODUCTS NATURAL LEFT JOIN INVENTORY ON products.prod_id = inventory.prod_id;

-- borramos la tabla de inventory y products, ya no nos hacen falta.
drop table inventory;
drop table products;

-- la renombramos de aux a products.
ALTER TABLE aux
RENAME TO products;

-- y establecemos sus anteriores propiedades (tenía dos claves) y el campo serial para el id.
ALTER TABLE products ADD CONSTRAINT prod_pkey PRIMARY KEY (prod_id);
ALTER TABLE products ADD CONSTRAINT prod_fkey FOREIGN KEY (movieid) REFERENCES imdb_movies (movieid);

CREATE SEQUENCE prod_id_seq
   OWNED by products.prod_id;

ALTER TABLE products
   ALTER COLUMN prod_id SET DEFAULT nextval('prod_id_seq');

BEGIN;
LOCK TABLE products IN EXCLUSIVE MODE;
select setval('prod_id_seq', COALESCE((SELECT MAX(prod_id) + 1 FROM products), 1), false);
COMMIT;


---------------------alerts-----------------------------
CREATE TABLE alerts (prod_id INTEGER REFERENCES products(prod_id));


---------------------orderdetail ------------------------
-- Establece las dos claves foráneas para la tabla orderdetail.
ALTER TABLE orderdetail ADD CONSTRAINT orderdetail_fk1 FOREIGN KEY (orderid) REFERENCES orders(orderid);

ALTER TABLE orderdetail ADD CONSTRAINT orderdetail_fk2 FOREIGN KEY (prod_id) REFERENCES products(prod_id);
