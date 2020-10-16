

-- Función que nos devuelve la cantidad de productos vendidos en cada año de cada producto.
-- DUda de por que ambiguo.

DROP FUNCTION IF EXISTS getVentas();

CREATE OR REPLACE FUNCTION getVentas() RETURNS TABLE (year INT, movie_id INT, sales NUMERIC) AS $$

   BEGIN

      RETURN QUERY SELECT EXTRACT(YEAR FROM orders.orderdate)::INT as year, products.movieid ,sum(orderdetail.quantity::NUMERIC) AS sales
      FROM orders INNER JOIN orderdetail ON orderdetail.orderid = orders.orderid
      INNER JOIN products ON orderdetail.prod_id = products.movieid
      GROUP BY EXTRACT(YEAR FROM orders.orderdate), products.movieid ORDER BY year DESC;

   END;
   $$ LANGUAGE plpgsql;



DROP FUNCTION IF EXISTS getTopVentasAnio();

CREATE OR REPLACE FUNCTION getTopVentasAnio() RETURNS TABLE (year INT, ventas NUMERIC) AS $$

   BEGIN
      RETURN QUERY SELECT Ventas.year, max(sales)
      FROM getVentas() AS Ventas
      GROUP BY Ventas.year;
   END;
   $$ LANGUAGE plpgsql;


DROP FUNCTION IF EXISTS getTopVentas(anio INT);
CREATE OR REPLACE FUNCTION getTopVentas(anio INT) RETURNS TABLE(year INT, peli VARCHAR, sales NUMERIC, movieid INT) AS $$

	BEGIN
		CREATE VIEW Ventas AS SELECT * FROM getVentas();
		CREATE VIEW VentasAnio AS SELECT * FROM getTopVentasAnio();
		RETURN QUERY SELECT VentasAnio.year, imdb_movies.movietitle, Ventas.sales, imdb_movies.movieid
		FROM VentasAnio INNER JOIN Ventas ON VentasAnio.ventas = Ventas.sales AND VentasAnio.year = Ventas.year INNER JOIN imdb_movies ON Ventas.movie_id=imdb_movies.movieid

		WHERE VentasAnio.year >= anio;
		DROP VIEW Ventas;
		DROP VIEW VentasAnio;

	END;
	$$ LANGUAGE plpgsql;



SELECT getTopVentas(2017);
