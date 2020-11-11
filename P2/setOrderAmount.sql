CREATE OR REPLACE FUNCTION setOrderAmount() 
RETURNS void AS $$
BEGIN
UPDATE orders
SET netamount = t.price,
    totalamount = t.price*(1+tax/100)
FROM(
    SELECT orderid, SUM(price) AS price FROM orderdetail
    GROUP BY orderid) AS t
WHERE 
    t.orderid = orders.orderid;
END;
$$ LANGUAGE plpgsql;
