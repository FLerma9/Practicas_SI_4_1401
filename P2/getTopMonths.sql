CREATE OR REPLACE FUNCTION getTopMonths (imp INT, prod INT)
RETURNS TABLE
(
    ANO DOUBLE PRECISION,
    MES DOUBLE PRECISION,
    IMPORTE NUMERIC,
    PRODUCTS BIGINT
)
      AS $$
BEGIN
RETURN QUERY
SELECT * FROM
(SELECT EXTRACT (year from orderdate) as anyo, EXTRACT (month from orderdate) as mes, SUM(totalamount) as Ite, SUM(quantity) as Pte
	     FROM orderdetail as ot, orders as o
	     WHERE ot.orderid = o.orderid
	     AND o.status is not null
	     GROUP BY anyo, mes) as aux
    WHERE Ite > $1
    AND Pte> $2;
END;
$$ LANGUAGE plpgsql;
