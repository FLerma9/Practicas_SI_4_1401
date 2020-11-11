UPDATE orderdetail
SET price=(p.price/POWER(1.02, EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM o.orderdate)))*orderdetail.quantity
FROM products as p, orders as o
WHERE p.prod_id=orderdetail.prod_id AND o.orderid=orderdetail.orderid;