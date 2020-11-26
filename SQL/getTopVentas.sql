CREATE OR REPLACE FUNCTION getTopVentas (anyo1 INT, anyo2 INT)
RETURNS TABLE
(
    ANO DOUBLE PRECISION,
    PELICULA CHARACTER VARYING(255),
    VENTAS NUMERIC
)
      AS $$
BEGIN
RETURN QUERY
SELECT * FROM
    (SELECT DISTINCT ON (anyo) EXTRACT (year from orderdate) as anyo , movietitle, SUM(quantity) as vent
          FROM imdb_movies as m, products as p, orderdetail as ot, orders as o
          WHERE m.movieid = p.movieid
                AND p.prod_id = ot.prod_id
                AND ot.orderid = o.orderid
                AND EXTRACT( year from o.orderdate) >= $1
                AND EXTRACT( year from o.orderdate) <= $2
                GROUP BY m.movieid, anyo
                ORDER BY anyo, vent DESC limit 100) as movies

          ORDER BY vent DESC;
END;
$$ LANGUAGE plpgsql;
