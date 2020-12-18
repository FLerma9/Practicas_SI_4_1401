CREATE INDEX ord_status
    ON orders (status);

ANALYZE orders;

explain analyze select count(*)
from orders
where status is null;

explain analyze select count(*)
from orders
where status = 'Shipped';

explain analyze select count(*)
from orders
where status = 'Paid';

explain analyze select count(*)
from orders
where status = 'Processed';
