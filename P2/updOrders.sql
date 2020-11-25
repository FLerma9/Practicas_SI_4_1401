DROP TRIGGER IF EXISTS updOrders ON orderdetail;
DROP FUNCTION IF EXISTS updOrders() CASCADE;
CREATE OR REPLACE FUNCTION updOrders() RETURNS TRIGGER AS $updOrders$
    BEGIN

    IF (TG_OP = 'DELETE') THEN
      IF ((SELECT DISTINCT orderid  FROM orderdetail WHERE orderid = OLD.orderid) IS NULL)
          THEN DELETE FROM orders WHERE orderid = OLD.orderid;
      RETURN NEW;
      END IF;

      UPDATE orders
      SET netamount = nuevo.sum,
          totalamount = nuevo.sum + nuevo.sum*(tax/100)
      FROM ((SELECT SUM (price*quantity) AS sum FROM orderdetail as o
              WHERE o.orderid = OLD.orderid)) AS nuevo
      WHERE orders.orderid = OLD.orderid;
      RETURN NEW;
    END IF;

    UPDATE orders
    SET netamount = nuevo.sum,
        totalamount = nuevo.sum + nuevo.sum*(tax/100)
    FROM ((SELECT SUM (price*quantity) AS sum FROM orderdetail as o
            WHERE o.orderid = NEW.orderid)) AS nuevo
    WHERE orders.orderid = NEW.orderid;

    RETURN NEW;
    END;
$updOrders$ LANGUAGE plpgsql;

CREATE TRIGGER opdOrders
AFTER INSERT OR UPDATE OR DELETE ON orderdetail
    FOR EACH ROW EXECUTE PROCEDURE updOrders();
