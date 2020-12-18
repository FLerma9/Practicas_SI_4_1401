ALTER TABLE customers ADD COLUMN promo INTEGER DEFAULT 0;

DROP FUNCTION IF EXISTS setPromo();
CREATE OR REPLACE FUNCTION setPromo() RETURNS TRIGGER AS $$
  BEGIN
    PERFORM pg_sleep(6);
    UPDATE orders SET netamount = aux.sum + aux.sum*(tax/100)
    FROM ((SELECT od.orderid AS id, SUM (price*quantity*(100 - NEW.promo)/100) AS sum
           FROM orders AS o, orderdetail AS od, customers AS c
           WHERE o.orderid = od.orderid AND c.customerid = o.customerid
           GROUP BY od.orderid)) AS aux
    WHERE o.orderid - aux.id AND o.status IS NULL AND o.customerid = NEW.customerid;
  RETURN NEW
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS updPromo ON customers;
CREATE TRIGGER updPromo AFTER UPDATE OF promo ON customers
    FOR EACH ROW EXECUTE PROCEDURE setPromo();
