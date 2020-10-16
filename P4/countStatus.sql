

EXPLAIN select count(*) from orders where status is null;



EXPLAIN select count(*) from orders where status ='Shipped';

DROP INDEX IF EXISTS indiced;
CREATE INDEX indiced
ON orders(status);

EXPLAIN select count(*) from orders where status is null;



EXPLAIN select count(*) from orders where status ='Shipped';

ANALYZE orders;

EXPLAIN select count(*) from orders where status is null;



EXPLAIN select count(*) from orders where status ='Shipped';
