DROP INDEX indice;
CREATE INDEX indice
ON orders(CAST(EXTRACT(month FROM orderdate) AS INT));




EXPLAIN
SELECT  COUNT ( DISTINCT customerid)
FROM orders
WHERE totalamount > 100 and EXTRACT(year FROM orderdate)::INT = 2015 and EXTRACT(month FROM orderdate)::INT = 04;
