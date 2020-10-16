DROP FUNCTION IF EXISTS setOrderAmountAux();

CREATE OR REPLACE FUNCTION setOrderAmountAux() RETURNS TABLE (orderid INT, price NUMERIC) AS $$


BEGIN

   RETURN QUERY SELECT orders.orderid, sum(orderdetail.price*orderdetail.quantity) AS price
   FROM orderdetail NATURAL JOIN orders
   GROUP BY orders.orderid;

END;
$$ LANGUAGE plpgsql;

DROP FUNCTION IF EXISTS setOrderAmount();

CREATE OR REPLACE FUNCTION setOrderAmount() RETURNS VOID AS $$

BEGIN
   UPDATE orders
   SET netamount = orderprice.price,
   totalamount = (orderprice.price*((100+tax)/100))
   FROM setOrderAmountAux() AS orderprice
   WHERE orderprice.orderid = orders.orderid;
END;
$$ LANGUAGE plpgsql;

SELECT setOrderAmount();
