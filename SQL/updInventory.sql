DROP TRIGGER IF EXISTS upd_Inventory ON orders;
DROP FUNCTION IF EXISTS upd_Inventory();
CREATE OR REPLACE FUNCTION updInventory() RETURNS TRIGGER AS $upd_Inventory$
    BEGIN
    UPDATE inventory
    SET stock  = stock - o.quantity, sales = sales + o.quantity
    FROM orderdetail AS o, orders
    WHERE o.prod_id = inventory.prod_id AND o.orderid = orders.orderid AND orders.orderid = OLD.orderid;


    INSERT INTO alertas(prod_id) (SELECT od.prod_id FROM orderdetail AS od, orders AS o, inventory AS i WHERE o.orderid = od.orderid
                                AND o.orderid = NEW.orderid AND od.prod_id = i.prod_id AND i.stock = 0);

      RETURN NEW;
    END;
$upd_Inventory$ LANGUAGE plpgsql;

CREATE TRIGGER upd_Inventory
AFTER UPDATE OF status ON orders
FOR EACH ROW WHEN (
    OLD.status IS NULL
    and NEW.status ='Paid') EXECUTE PROCEDURE updInventory();
