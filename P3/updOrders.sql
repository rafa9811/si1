DROP TRIGGER IF EXISTS updOrders on orderdetail;

DROP FUNCTION IF EXISTS updOrdersFunction();
CREATE FUNCTION updOrdersFunction() RETURNS TRIGGER AS $$

BEGIN
   IF TG_OP = 'INSERT' THEN
   -- Es un insert
   -- En este caso, tenemos un nuevo artículo que hemos añadido. Hemos de tener en cuenta que puede que la compra que
   -- añadimos hemos de calcular su precio con set price, y luego ya recalculamos el precio total del orders.
      UPDATE orderdetail
      SET price = products.price * POW(0.98, 2019 - EXTRACT(YEAR FROM orders.orderdate))::NUMERIC
      FROM products, orders
      WHERE orders.orderid = NEW.orderid AND products.prod_id = orderdetail.prod_id AND orders.orderid = orderdetail.orderid;
      UPDATE orders
      SET netamount = orderprice.price,
      totalamount = orderprice.price*((100+tax)/100)
      FROM (SELECT orders.orderid, sum(orderdetail.price*orderdetail.quantity) AS price
      FROM orderdetail INNER JOIN orders ON orderdetail.orderid = orders.orderid
      -- Aquí, a través de OLD, es como obtenemos las filas de orderdetail que son de este pedido que hay que calcular.
      WHERE orderdetail.orderid = NEW.orderid
      GROUP BY orders.orderid) AS orderprice
      WHERE orderprice.orderid = orders.orderid;
      RETURN NEW;

   ELSIF TG_OP = 'UPDATE' THEN
         -- Es un update. Por tanto, hemos de realizar casi lo mismo que hicimos en setOrderAmount
         -- Es decir, hemos de recalcular el precio netamount y totalamount del order del que acabamos de actualizar el número.
         -- ya que o bien tendremos más de él, o no y por tanto el precio varía.
         -- ¿Se puede hacer un update poniendo todo a cero? Si es así deberíamos pensarlo.
      UPDATE orders
      SET netamount = orderprice.price,
      totalamount = orderprice.price*((100+tax)/100)
      FROM (SELECT orders.orderid, sum(orderdetail.price*orderdetail.quantity) AS price
      FROM orderdetail INNER JOIN orders ON orderdetail.orderid = orders.orderid
      -- Aquí, a través de OLD, es como obtenemos las filas de orderdetail que son de este pedido que hay que calcular.
      WHERE orderdetail.orderid = NEW.orderid
      GROUP BY orders.orderid) AS orderprice
      WHERE orderprice.orderid = orders.orderid;
         RETURN NEW;
   ELSIF TG_OP = 'DELETE' THEN
   -- Es un delete. Por tanto, hemos de realizar casi lo mismo que hicimos en setOrderAmount
   -- Es decir, hemos de recalcular el precio netamount y totalamount del order del que acabamos de borrar un producto.
	UPDATE orders
      SET netamount = orderprice.price,
      totalamount = orderprice.price*((100+tax)/100)
      FROM (SELECT orders.orderid, sum(orderdetail.price*orderdetail.quantity) AS price
      FROM orderdetail INNER JOIN orders ON orderdetail.orderid = orders.orderid
      -- Aquí, a través de OLD, es como obtenemos las filas de orderdetail que son de este pedido que hay que calcular.
      WHERE orderdetail.orderid = OLD.orderid
      GROUP BY orders.orderid) AS orderprice
      WHERE orderprice.orderid = orders.orderid;
      RETURN OLD;

   END IF;

END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER updOrders
   -- Cuando añadimos o eliminimos algo al carrito, estaremos relacionando un producto con un order, es decir,
   -- estaremos modificando la tabla orderdetail. Por tanto, hemos de comprobar en esta si se ha producido algún evento.
   AFTER UPDATE OR INSERT OR DELETE ON orderdetail
   -- Queremos que se active una vez para cada fila modificada.
   FOR EACH ROW
   EXECUTE PROCEDURE updOrdersFunction();
