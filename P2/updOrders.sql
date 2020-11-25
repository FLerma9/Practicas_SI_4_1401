CREATE OR REPLACE FUNCTION updOrders() RETURNS TRIGGER AS $upd_Orders$
    BEGIN

      PERFORM * FROM setOrderAmount();

    END;
$upd_Orders$ LANGUAGE plpgsql;

CREATE TRIGGER upd_Orders
AFTER INSERT OR UPDATE OR DELETE ON orderdetail
    FOR EACH ROW EXECUTE PROCEDURE updOrders();
