DROP TRIGGER IF EXISTS updInventory ON orders;
DROP TABLE IF EXISTS alerts;
CREATE TABLE alerts (prod_id INTEGER REFERENCES products(prod_id));
DROP FUNCTION IF EXISTS updInventoryFunction();
CREATE OR REPLACE FUNCTION updInventoryFunction()
RETURNS TRIGGER AS $$

  BEGIN
    IF NEW.status = 'Paid' THEN
      UPDATE products
        SET stock= GREATEST(0, products.stock - orderdetail.quantity), sales = products.sales + orderdetail.quantity
        FROM orderdetail
        WHERE NEW.orderid = orderdetail.orderid AND products.prod_id = orderdetail.prod_id;

    -- Almacenamos en alertas aquellos productos cuyo stock se haya quedado a cero tras actualizar sus ventas.
    INSERT INTO alerts
    SELECT products.prod_id
    FROM products  INNER JOIN orderdetail ON products.prod_id = products.prod_id
    WHERE NEW.orderid = orderdetail.orderid AND products.stock = 0;

    END IF;
    RETURN NEW;
  END;
  $$ LANGUAGE plpgsql;



CREATE TRIGGER updInventory
  AFTER UPDATE OF status ON orders
  FOR EACH ROW
  EXECUTE PROCEDURE updInventoryFunction();
