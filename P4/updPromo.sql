ALTER TABLE customers ADD COLUMN promo int;



DROP TRIGGER IF EXISTS updPromos on orderdetail;

DROP FUNCTION IF EXISTS updPromosFunction();
CREATE FUNCTION updPromosFunction() RETURNS TRIGGER AS $$

BEGIN
   UPDATE orderdetail
   SET price = (orderdetail.price - orderdetail.price*NEW.promo)
   FROM orders
   WHERE orderdetail.orderid = orders.orderid AND AND orders.customerid = OLD.customerid orders.status is NULL;


PERFORM pg_sleep(60);
RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER updPromos
   -- Cuando añadimos o eliminimos algo al carrito, estaremos relacionando un producto con un order, es decir,
   -- estaremos modificando la tabla orderdetail. Por tanto, hemos de comprobar en esta si se ha producido algún evento.
   AFTER UPDATE ON customers
   -- Queremos que se active una vez para cada fila modificada.
   FOR EACH ROW
   EXECUTE PROCEDURE updPromosFunction();



--TODO: Añadir carritos con NULL.
