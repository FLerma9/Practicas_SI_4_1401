CREATE OR REPLACE FUNCTION updOrders() RETURNS TRIGGER AS $updOrders$
    BEGIN

      PERFORM * FROM setOrderAmount();

    END;
$upd_Orders$ LANGUAGE plpgsql;

CREATE TRIGGER updOrders
AFTER INSERT OR UPDATE OR DELETE ON orderdetail
    FOR EACH ROW EXECUTE PROCEDURE updOrders();
