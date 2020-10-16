--Sabiendo que los precios de las películas se han ido incrementando un 2% anualmente,
--elaborar la consulta setPrice.sql que complete la columna 'price' de la tabla
--'orderdetail', sabiendo que el precio actual es el de la tabla 'products'.
UPDATE orderdetail
SET price = (products.price * POW(0.98, 2019 - EXTRACT(YEAR FROM orders.orderdate)))::NUMERIC
FROM products, orders
WHERE products.prod_id = orderdetail.prod_id AND orders.orderid = orderdetail.orderid;

SELECT PRICE FROM PRODUCTS
