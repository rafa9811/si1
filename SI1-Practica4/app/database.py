# -*- coding: utf-8 -*-

import os
import sys, traceback, time

from sqlalchemy import create_engine

# configurar el motor de sqlalchemy
db_engine = create_engine("postgresql://alumnodb:alumnodb@localhost/si1", echo=False, execution_options={"autocommit":False})

def dbConnect():
    return db_engine.connect()

def dbCloseConnect(db_conn):
    db_conn.close()

def getListaCliMes(db_conn, mes, anio, iumbral, iintervalo, use_prepare, break0, niter):

    db_conn = None
    db_conn = db_engine.connect()
    #db_conn.execute("DROP IF EXISTS getListaCliMes")
    consulta_prepare = f"PREPARE getListaCliMes(int, int, int) AS SELECT  COUNT ( DISTINCT customerid) FROM orders WHERE totalamount > $1 and EXTRACT(year FROM orderdate)::INT = $2 and EXTRACT(month FROM orderdate)::INT = $3;"

    db_result = db_conn.execute(consulta_prepare)





    # TODO: ejecutar la consulta
    # - mediante PREPARE, EXECUTE, DEALLOCATE si use_prepare es True
    # - mediante db_conn.execute() si es False
    if use_prepare:
        db_conn.execute(consulta_prepare)
    # Array con resultados de la consulta para cada umbral
    dbr=[]

    for ii in range(niter):
        if use_prepare:
            res = list(db_conn.execute(f"EXECUTE getListaCliMes({iumbral},{anio},{mes})"))
            db_conn.execute("DEALLOCATE getListaCliMes;")
            dbr.append({"umbral":iumbral,"contador":res[0][0]})
        else:
            res = list(db_conn.execute(f"SELECT  COUNT ( DISTINCT customerid) FROM orders WHERE totalamount > {iumbral} and EXTRACT(year FROM orderdate)::INT = {anio} and EXTRACT(month FROM orderdate)::INT = {mes};"))
            # Guardar resultado de la query
            dbr.append({"umbral":iumbral,"contador":res[0][0]})

            # TODO: si break0 es True, salir si contador resultante es cero
            if(break0 and res[0]==0):
                break
            # Actualizacion de umbral
            iumbral = iumbral + iintervalo

    db_conn.close()
    return dbr

def getMovies(anio):
    # conexion a la base de datos
    db_conn = db_engine.connect()

    query="select movietitle from imdb_movies where year = '" + anio + "'"
    resultproxy=db_conn.execute(query)

    a = []
    for rowproxy in resultproxy:
        d={}
        # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
        for tup in rowproxy.items():
            # build up the dictionary
            d[tup[0]] = tup[1]
        a.append(d)

    resultproxy.close()

    db_conn.close()

    return a

def getCustomer(username, password):
    # conexion a la base de datos
    db_conn = db_engine.connect()

    query="select * from customers where username='" + username + "' and password='" + password + "'"
    res=db_conn.execute(query).first()

    db_conn.close()

    if res is None:
        return None
    else:
        return {'firstname': res['firstname'], 'lastname': res['lastname']}

def delCustomer(customerid, bFallo, bSQL, duerme, bCommit):

    # Array de trazas a mostrar en la página
    dbr=[]
    db_conn = db_engine.connect()
    # TODO: Ejecutar consultas de borrado
    # - ordenar consultas según se desee provocar un error (bFallo True) o no
    # - ejecutar commit intermedio si bCommit es True
    # - usar sentencias SQL ('BEGIN', 'COMMIT', ...) si bSQL es True
    # - suspender la ejecución 'duerme' segundos en el punto adecuado para forzar deadlock
    # - ir guardando trazas mediante dbr.append()


    try:
        if bSQL:
            db_conn.execute('BEGIN;')
        else:
            transaccion = db_conn.begin()
            dbr.append("Ya está hecho el begin.")
        #Ahora es cuando hemos de realizar los pasos bien, ya que no queremos que haya fallo.
        if not bFallo:
            #En este caso, como no vamos a hacer commit ni nada, no es necesario ver si hay bsql o no.
            consulta = f"DELETE FROM orderdetail USING orders WHERE orderdetail.orderid = orders.orderid AND orders.customerid = '{customerid}'"
            db_conn.execute(consulta)
            #Aquí dormimos para provocar el deadlock.
            time.sleep(duerme)
            dbr.append("Hemos eliminado todas las filas de orderdetail relacionadas con pedidos hechos por este usuario.")
            consulta = f"DELETE FROM orders WHERE orders.customerid = '{customerid}'"
            db_conn.execute(consulta)
            dbr.append("Hemos eliminado los pedidos realizados por el usuario")
            consulta = f"DELETE FROM customers WHERE customerid = '{customerid}'"
            db_conn.execute(consulta)
            dbr.append("Hemos eliminado al usuario")


        else:
            #Miramos si hemos de hacerlo con sentencias SQL.

            consulta = f"DELETE FROM orderdetail USING orders WHERE orderdetail.orderid = orders.orderid AND orders.customerid = '{customerid}'"
            db_conn.execute(consulta)
            #Aquí es cuando dormimos para provocar el deadlock.
            time.sleep(duerme)
            dbr.append("Hemos eliminado todas las filas de orderdetail relacionadas con pedidos hechos por este usuario.")
            #Hasta ahora está bien, por lo que realizamos un commit si queremos que se haga. Comprobamos también
            #bsql.
            if bCommit and bSQL:
                consulta = "COMMIT;"
                db_conn.execute(consulta)
                dbr.append("Ya se ha realizado el commit.")
                consulta = "BEGIN;"
                transaccion = db_conn.execute(consulta)
            if bCommit and not bSQL:
                transaccion.commit()
                transaccion = db_conn.begin()
                dbr.append("Ya se ha realizado el commit.")

            #Ahora es cuando eliminamos el usuario antes de los pedidos, por lo que debería dar fallo.
            dbr.append("Vamos a eliminar al usuario.")
            consulta = f"DELETE FROM customers WHERE customerid = '{customerid}'"
            db_conn.execute(consulta)
            dbr.append("Hemos eliminado al usuario")
            consulta = f"DELETE FROM orders WHERE orders.customerid = '{customerid}'"
            db_conn.execute(consulta)
            dbr.append("Hemos eliminado los pedidos realizados por el usuario")











        # TODO: ejecutar consultas

    except Exception as e:
        # TODO: deshacer en caso de error
        dbr.append("Ha habido un error. Realizando ROLLBACK")
        dbr.append(f"Fallo: {e}")
        if bSQL:
            db_conn.execute("ROLLBACK;")
        else:
            transaccion.rollback()

        dbr.append("Se ha realizado el rollback.")
        #Vamos a comprobar que realmente nos hemos quedado en el commit.Es decir, que no hay ningún pedido.
        consulta = f"SELECT orderid FROM orderdetail NATURAL JOIN orders WHERE orders.customerid = '{customerid}'"
        pedidos = list(db_conn.execute(consulta))
        #Vemos que no hay ninguno.
        if(len(pedidos)==0):
            dbr.append("No hay pedidos del usuario.")
        else:
            dbr.append("Hay pedidos")

    else:
    # TODO: confirmar cambios si todo va bien
    #Hacemos commit porque todo ha ido bien.

        dbr.append("Todo ha ido bien. HAciendo commit.")
        if bSQL:
            db_conn.execute("COMMIT;")
        else:
            transaccion.commit()

        db_conn.close()



    return dbr
