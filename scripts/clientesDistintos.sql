CREATE INDEX ord_orders
   ON orders (EXTRACT( year from orderdate), EXTRACT( month from orderdate));

CREATE INDEX ord_year
    ON orders (EXTRACT( year from orderdate));

CREATE INDEX ord_month
    ON orders (EXTRACT( month from orderdate));

CREATE INDEX ord_status
    ON orders (status);


SELECT COUNT ( DISTINCT c.customerid ) as clientes
    FROM orders as o, customers as c
    WHERE o.customerid = c.customerid AND
    EXTRACT( year from o.orderdate) = 2015 AND
    EXTRACT( month from o.orderdate) = 04 AND
    100 <= o.totalamount;
