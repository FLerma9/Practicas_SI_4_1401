DROP TRIGGER IF EXISTS upd_Inventory ON orders;
DROP FUNCTION IF EXISTS upd_Inventory();
CREATE OR REPLACE FUNCTION updInventory() RETURNS TRIGGER AS $upd_Inventory$
    BEGIN
      IF ((SELECT stock FROM inventory, orderdetail AS o, orders
        WHERE o.prod_id = inventory.prod_id AND o.orderid = orders.orderid AND orders.orderid = OLD.orderid) = 0) THEN
        INSERT INTO alertas VALUES((SELECT prod_id FROM orderdetail AS o, orders WHERE o.orderid = orders.orderid AND orders.orderid = OLD.orderid));

      ELSE
        UPDATE inventory
        SET stock  = stock - o.quantity, sales = sales + o.quantity
        FROM orderdetail AS o, orders
        WHERE o.prod_id = inventory.prod_id AND o.orderid = orders.orderid AND orders.orderid = OLD.orderid;
      END IF;

      RETURN NEW;
    END;
$upd_Inventory$ LANGUAGE plpgsql;

CREATE TRIGGER upd_Inventory
AFTER UPDATE OF status ON orders
FOR EACH ROW WHEN (
    OLD.status IS NULL
    and NEW.status ='Paid') EXECUTE PROCEDURE updInventory();
