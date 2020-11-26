CREATE OR REPLACE FUNCTION getTopMonths (imp INT, prod INT)
RETURNS TABLE
(
    ANO DOUBLE PRECISION,
    MES DOUBLE PRECISION,
    IMPORTE NUMERIC,
    PRODUCTS NUMERIC
)
      AS $$
BEGIN
RETURN QUERY
SELECT * FROM
(SELECT EXTRACT (year from orderdate) as anyo, EXTRACT (month from orderdate) as mes, SUM(totalamount) as Ite, SUM(sumquantity) as Pte
	     FROM orders as o INNER JOIN (
			SELECT orderid, SUM(quantity) AS sumquantity
			FROM orderdetail
			GROUP BY orderid
			) AS quantitytable ON quantitytable.orderid=o.orderid
	     WHERE o.status is not null
	     GROUP BY anyo, mes) as aux
WHERE Ite > $1 OR Pte> $2;
END;
$$ LANGUAGE plpgsql;
