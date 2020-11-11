CREATE OR REPLACE FUNCTION updInventory() RETURNS TRIGGER AS $upd_Inventory$
    BEGIN
      UPDATE inventory SET stock = stock - o.quantity, sales = sales + o.quantity
      FROM orderdetail AS o
      WHERE o.prod_id = inventory.prod_id;

      INSERT INTO alertas(prod_id)
      SELECT prod_id FROM inventory WHERE stock == 0;

    END;
$upd_Inventory$ LANGUAGE plpgsql;

CREATE TRIGGER upd_Inventory
AFTER UPDATE OF status ON orders
FOR EACH ROW WHEN (
    OLD.status IS NULL
    and NEW.status ='Paid') EXECUTE PROCEDURE updInventory();
