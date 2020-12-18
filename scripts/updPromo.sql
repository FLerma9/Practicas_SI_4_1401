ALTER TABLE customers ADD COLUMN promo INTEGER DEFAULT 0;

DROP FUNCTION IF EXISTS setPromo();
CREATE OR REPLACE FUNCTION setPromo() RETURNS TRIGGER AS $$
  BEGIN
    PERFORM pg_sleep(6);
    UPDATE orders SET netamount = aux.sum,
    totalamount = aux.sum + aux.sum*(tax/100)
    FROM ((SELECT orderdetail.orderid AS id, SUM (price*quantity*(100 - NEW.promo)/100) AS sum
           FROM orders, orderdetail, customers
           WHERE orders.orderid = orderdetail.orderid AND customers.customerid = orders.customerid
           GROUP BY orderdetail.orderid)) AS aux
    WHERE orders.orderid = aux.id AND orders.status IS NULL AND orders.customerid = NEW.customerid;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS updPromo ON customers;
CREATE TRIGGER updPromo AFTER UPDATE OF promo ON customers
    FOR EACH ROW EXECUTE PROCEDURE setPromo();
