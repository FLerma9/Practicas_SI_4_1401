-- TABLA CUSTOMERS
UPDATE customers SET username=CONCAT(username, CAST(customerid AS VARCHAR))
WHERE customerid NOT IN (
  SELECT MIN(customerid)
  FROM customers
  GROUP BY username
);

CREATE UNIQUE INDEX CONCURRENTLY customers_username
ON customers(username);

ALTER TABLE customers
ALTER address1 DROP not null,
ALTER city DROP not null,
ALTER firstname DROP not null,
ALTER lastname DROP not null,
ALTER country DROP not null,
ALTER region DROP not null,
ALTER email SET NOT NULL,
ALTER creditcardtype DROP not null,
ALTER creditcardexpiration DROP not null,
ALTER zip TYPE integer USING zip::integer,
ADD CONSTRAINT unique_username UNIQUE USING INDEX customers_username;

-- TABLA MOVIES
ALTER TABLE imdb_actormovies
ADD CONSTRAINT imdb_actormovies_pkey PRIMARY KEY (actorid, movieid),
ADD CONSTRAINT  imdb_actormovies_actorid_fkey FOREIGN KEY (actorid) REFERENCES imdb_actors(actorid) ON UPDATE CASCADE ON DELETE CASCADE,
ADD CONSTRAINT  imdb_actormovies_movieid_fkey FOREIGN KEY (movieid) REFERENCES imdb_movies(movieid) ON UPDATE CASCADE ON DELETE CASCADE,
ALTER isvoice DROP DEFAULT,
ALTER isvoice TYPE bool USING (isvoice::int::bool),
ALTER isvoice SET NOT NULL,
ALTER isvoice SET DEFAULT false,
ALTER isarchivefootage DROP DEFAULT,
ALTER isarchivefootage TYPE bool USING (isarchivefootage::int::bool),
ALTER isarchivefootage SET NOT NULL,
ALTER isarchivefootage SET DEFAULT false,
ALTER isuncredited DROP DEFAULT,
ALTER isuncredited TYPE bool USING (isuncredited::int::bool),
ALTER isuncredited SET NOT NULL,
ALTER isuncredited SET DEFAULT false;

-- TABLA DIRECTORMOVIES
ALTER TABLE imdb_directormovies
DROP CONSTRAINT  imdb_directormovies_pkey,
ADD CONSTRAINT imdb_directormovies_pkey PRIMARY KEY (directorid, movieid),
DROP CONSTRAINT  imdb_directormovies_directorid_fkey,
ADD CONSTRAINT imdb_directormovies_directorid_fkey FOREIGN KEY (directorid) REFERENCES imdb_directors(directorid) ON UPDATE CASCADE ON DELETE CASCADE,
DROP CONSTRAINT  imdb_directormovies_movieid_fkey,
ADD CONSTRAINT imdb_directormovies_movieid_fkey FOREIGN KEY (movieid) REFERENCES imdb_movies(movieid) ON UPDATE CASCADE ON DELETE CASCADE,
ALTER directorid DROP DEFAULT,
ALTER movieid DROP DEFAULT,
ALTER isarchivefootage DROP DEFAULT,
ALTER isarchivefootage TYPE bool USING (isarchivefootage::int::bool),
ALTER isarchivefootage SET NOT NULL,
ALTER isarchivefootage SET DEFAULT false,
ALTER isuncredited DROP DEFAULT,
ALTER isuncredited TYPE bool USING (isuncredited::int::bool),
ALTER isuncredited SET NOT NULL,
ALTER isuncredited SET DEFAULT false,
ALTER iscodirector DROP DEFAULT,
ALTER iscodirector TYPE bool USING (iscodirector::int::bool),
ALTER iscodirector SET NOT NULL,
ALTER iscodirector SET DEFAULT false,
ALTER ispilot DROP DEFAULT,
ALTER ispilot TYPE bool USING (ispilot::int::bool),
ALTER ispilot SET NOT NULL,
ALTER ispilot SET DEFAULT false,
ALTER iscodirector SET DEFAULT false,
ALTER ischief DROP DEFAULT,
ALTER ischief TYPE bool USING (ischief::int::bool),
ALTER ischief SET NOT NULL,
ALTER ischief SET DEFAULT false,
ALTER ishead DROP DEFAULT,
ALTER ishead TYPE bool USING (ishead::int::bool),
ALTER ishead SET NOT NULL,
ALTER ishead SET DEFAULT false;

-- TABLA COUNTRIES MOVIECOUNTRIES
CREATE SEQUENCE countries_countryid_seq;
CREATE TABLE countries(
  countryid integer NOT NULL DEFAULT nextval('countries_countryid_seq'),
  country character varying(32) NOT NULL,
  CONSTRAINT countries_pkey PRIMARY KEY (countryid)
);

INSERT INTO countries (country)
SELECT DISTINCT country FROM imdb_moviecountries;

CREATE SEQUENCE imdb_moviecountries_countryid_seq;

ALTER TABLE imdb_moviecountries
ADD COLUMN countryid integer,
ALTER movieid DROP DEFAULT,
DROP CONSTRAINT  imdb_moviecountries_movieid_fkey,
ADD CONSTRAINT imdb_moviecountries_movieid_fkey FOREIGN KEY (movieid) REFERENCES imdb_movies(movieid) ON UPDATE CASCADE ON DELETE CASCADE,
ADD CONSTRAINT imdb_moviecountries_countryid_fkey FOREIGN KEY (countryid) REFERENCES countries(countryid) ON UPDATE CASCADE ON DELETE CASCADE;

UPDATE imdb_moviecountries
SET countryid = t.countryid
FROM countries as t
WHERE t.country = imdb_moviecountries.country;

ALTER TABLE imdb_moviecountries
DROP COLUMN country,
ADD CONSTRAINT imdb_moviecountries_pkey PRIMARY KEY (movieid, countryid);

-- TABLA GENRES MOVIEGENRES
CREATE SEQUENCE genres_genreid_seq;
CREATE TABLE genres(
  genresid integer NOT NULL DEFAULT nextval('genres_genreid_seq'),
  genre character varying(32) NOT NULL,
  CONSTRAINT genres_pkey PRIMARY KEY (genresid)
);

INSERT INTO genres (genre)
SELECT DISTINCT genre FROM imdb_moviegenres;


ALTER TABLE imdb_moviegenres
ADD COLUMN genresid integer,
ALTER movieid DROP DEFAULT,
DROP CONSTRAINT  imdb_moviegenres_movieid_fkey,
ADD CONSTRAINT imdb_moviegenres_movieid_fkey FOREIGN KEY (movieid) REFERENCES imdb_movies(movieid) ON UPDATE CASCADE ON DELETE CASCADE,
ADD CONSTRAINT imdb_moviegenres_genresid_fkey FOREIGN KEY (genresid) REFERENCES genres(genresid) ON UPDATE CASCADE ON DELETE CASCADE;

UPDATE imdb_moviegenres
SET genresid = t.genresid
FROM genres as t
WHERE t.genre = imdb_moviegenres.genre;

ALTER TABLE imdb_moviegenres
DROP COLUMN genre,
ADD CONSTRAINT imdb_moviegenres_pkey PRIMARY KEY (movieid, genresid);

-- TABLA LANGUAGES MOVIELANGUAGES
CREATE SEQUENCE languages_languageid_seq;
CREATE TABLE languages(
  languageid integer NOT NULL DEFAULT nextval('languages_languageid_seq'),
  language character varying(32) NOT NULL,
  CONSTRAINT languages_pkey PRIMARY KEY (languageid)
);

INSERT INTO languages (language)
SELECT DISTINCT language FROM imdb_movielanguages;


ALTER TABLE imdb_movielanguages
ADD COLUMN languageid integer,
DROP CONSTRAINT  imdb_movielanguages_movieid_fkey,
ADD CONSTRAINT imdb_movielanguages_movieid_fkey FOREIGN KEY (movieid) REFERENCES imdb_movies(movieid) ON UPDATE CASCADE ON DELETE CASCADE,
ADD CONSTRAINT imdb_movielanguages_languageid_fkey FOREIGN KEY (languageid) REFERENCES languages(languageid) ON UPDATE CASCADE ON DELETE CASCADE;

UPDATE imdb_movielanguages
SET languageid = t.languageid
FROM languages as t
WHERE t.language = imdb_movielanguages.language;

ALTER TABLE imdb_movielanguages
DROP COLUMN language,
ADD CONSTRAINT imdb_movielanguages_pkey PRIMARY KEY (movieid, languageid);


-- TABLA MOVIES
ALTER TABLE imdb_movies
ALTER year SET NOT NULL,
ALTER issuspended DROP DEFAULT,
ALTER issuspended TYPE bool USING (issuspended::int::bool),
ALTER issuspended SET NOT NULL,
ALTER issuspended SET DEFAULT false;

-- TABLA INVENTORY
ALTER TABLE inventory
ADD CONSTRAINT inventory_prod_id_fkey FOREIGN KEY (prod_id) REFERENCES products(prod_id) ON UPDATE CASCADE ON DELETE CASCADE,
ADD CONSTRAINT valid_stock CHECK (stock >= 0),
ADD CONSTRAINT valid_sales CHECK (sales >= 0);

-- TABLA ORDERDETAIL
SELECT orderid, prod_id, SUM(price) AS price, SUM(quantity) AS quantity
INTO temporal
FROM orderdetail
GROUP BY orderid, prod_id;

DROP TABLE orderdetail;

ALTER TABLE temporal RENAME TO orderdetail;

ALTER TABLE orderdetail
ADD CONSTRAINT orderdetail_pkey PRIMARY KEY (orderid, prod_id),
ADD CONSTRAINT orderdetail_orderid_fkey FOREIGN KEY (orderid) REFERENCES orders(orderid) ON UPDATE CASCADE ON DELETE CASCADE,
ADD CONSTRAINT orderdetail_prod_id_fkey FOREIGN KEY (prod_id) REFERENCES products(prod_id) ON UPDATE CASCADE ON DELETE CASCADE,
ADD CONSTRAINT valid_quantity CHECK (quantity >= 0);

-- TABLA ORDERS
ALTER TABLE orders
ALTER orderdate SET DEFAULT now(),
ALTER customerid SET NOT NULL,
ALTER tax SET DEFAULT 0,
ADD CONSTRAINT orders_customerid_fkey FOREIGN KEY (customerid) REFERENCES customers(customerid) ON UPDATE CASCADE ON DELETE CASCADE,
ADD CONSTRAINT valid_tax CHECK (tax >= 0);

-- TABLA PRODUCTS
ALTER TABLE products
DROP CONSTRAINT products_movieid_fkey,
ADD CONSTRAINT products_movieid_fkey FOREIGN KEY (movieid) REFERENCES imdb_movies(movieid) ON UPDATE CASCADE ON DELETE CASCADE;

-- TABLA ALERTAS
CREATE SEQUENCE alert_seq;
CREATE TABLE alertas (
  alertid integer NOT NULL DEFAULT nextval('alert_seq'::regclass),
  prod_id integer NOT NULL,
  CONSTRAINT alertas_pkey PRIMARY KEY (alertid),
  CONSTRAINT alertas_prod_id_fkey FOREIGN KEY (prod_id) REFERENCES products(prod_id) ON UPDATE CASCADE ON DELETE CASCADE
);

ALTER SEQUENCE imdb_actors_actorid_seq RESTART WITH 1150441;
ALTER SEQUENCE imdb_directors_directorid_seq RESTART WITH 117481;
ALTER SEQUENCE imdb_movies_movieid_seq RESTART WITH 774326;
ALTER SEQUENCE products_prod_id_seq RESTART WITH 6657;
ALTER SEQUENCE customers_customerid_seq RESTART WITH 14094;
ALTER SEQUENCE orders_orderid_seq RESTART WITH 181791;
