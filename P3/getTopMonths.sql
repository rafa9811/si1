DROP FUNCTION IF EXISTS getTopMonthsAux();
CREATE OR REPLACE FUNCTION getTopMonthsAux() RETURNS TABLE(year INT, month INT, totalamount NUMERIC, nprods BIGINT)
AS $$

BEGIN
   RETURN QUERY
   SELECT EXTRACT (YEAR FROM orders.orderdate)::INT AS year, EXTRACT (MONTH FROM orders.orderdate)::INT AS month,
   sum(orders.totalamount), sum(quantity)
   FROM orders NATURAL JOIN orderdetail GROUP BY year, month;

END;
$$ LANGUAGE plpgsql;



DROP FUNCTION IF EXISTS getTopMonths(INT, INT);
CREATE OR REPLACE FUNCTION getTopMonths(start_nprods INT, start_totalamount INT) RETURNS TABLE(year INT, month INT, totalamount NUMERIC, nprods BIGINT)
AS $$

BEGIN
	RETURN QUERY
	SELECT TopMonthsAux.*
	FROM getTopMonthsAux() AS TopMonthsAux
	WHERE TopMonthsAux.nprods > start_nprods OR TopMonthsAux.totalamount > start_totalamount::NUMERIC;

END;
$$ LANGUAGE plpgsql;

SELECT getTopMonths(19000, 320000);
