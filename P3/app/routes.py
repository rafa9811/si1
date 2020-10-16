#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app
from flask import render_template, request, url_for, redirect, session, make_response
import json
import os
import sys, traceback
import crypt
import random
import pickle
import datetime
from hmac import compare_digest as compare_hash
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, text
from sqlalchemy.sql import select

db_engine = create_engine("postgresql://alumnodb:alumnodb@localhost/si1", echo=False)
db_meta = MetaData(bind=db_engine)
db_table_customers = Table('customers', db_meta, autoload=True, autoload_with=db_engine)



#Funciones de encriptar contraseñas en md5 con salt.
def encryptMD5(password):
    #CRYPT utiliza un salt aleatorio en MD5 cada vez que le llamamos.
    hash = crypt.crypt(password, crypt.METHOD_MD5)
    return hash


def checkPassword(password, hash):
    #Puesto que el salt cada vez es aleatorio, para obtener un mismo hash de una contraseña plana
    #hemos de introducir como segundo parámetro el hash que obtuvimos previamente, y ya comparamos.
    return compare_hash(crypt.crypt(password, hash), hash)


#Funciones auxiliares:
def obtener_saldo():
    ruta = os.path.join(app.root_path,'usuarios/' + session['usuario'] + '/datos.dat')
    if os.path.isfile(ruta):

        with  open(ruta, 'rb') as info_data:
            info = pickle.load(info_data)

        saldo_usuario=float(info['saldo'])

        return saldo_usuario, ruta


def comprar(precio):
    saldo_usuario, ruta = obtener_saldo()
    if(precio > saldo_usuario):
        return "ERROR"
    else:
        saldo_usuario = saldo_usuario - precio
        actualizar_saldo(ruta, saldo_usuario)


def actualizar_saldo(ruta, saldo):

    with  open(ruta, 'rb') as info_data:
        info = pickle.load(info_data)

    info['saldo'] = str(saldo)

    with  open(ruta, 'wb') as info_data:
        pickle.dump(info, info_data)




def sumar_saldo(saldo):
    saldo_usuario, ruta = obtener_saldo()
    nuevo_saldo = saldo_usuario + float(saldo)
    actualizar_saldo(ruta, nuevo_saldo)

def topventas_database():
    ##Obtenemos las películas más vistas. Cogemos un producto de cada una de ellas y lo ponemos."
    try:
        db_conn = None
        db_conn = db_engine.connect()
        query_topventas = f"SELECT * FROM getTopVentas(2016);"


        db_result = db_conn.execute(query_topventas)


        return list(db_result)
    except:
        if db_conn is not None:
            db_conn.close()
        return(None)

    # try:
    #     listprodfilms = []
    #     ##Queremos mostrar un producto de cada película más vendida, por lo que:
    #     # for film in list(db_result1):
    #     #     #Cogemos el primer producto resultado asociado al movie_id:
    #     # query_topventasprod = f"SELECT imdb_movies.titlename, imdb_movies.year, imdb_movies.movieid, products.prod_id FROM imdb_movies INNER JOIN products ON imdb_movies.prod_id = products.prod_id"
    #     # + " WHERE imdb_movies.titlename = '{film[1]}';"
    #     # print(query_topventasprod)
    #     # db_result2 = db_conn.execute(query_topventasprod)
    #     #
    #     # listprodfilms.append(list(db_result2)[0])
    #     return listprodfilms
    # except:
    #     if db_conn is not None:
    #         db_conn.close()
    #     return(None)


#Funciones de vista:
@app.route('/')
@app.route('/index')
def index():
    catalogue_data = open(os.path.join(app.root_path,'catalogue/catalogo.json'), encoding="utf-8").read()
    catalogue = json.loads(catalogue_data)
    # novedades = []
    # for m in catalogue['peliculas']:
    #     if m['novedad'] == 'Sí':
    #         novedades.append(m)
    categoria_data = open(os.path.join(app.root_path,'catalogue/categoria.json'), encoding="utf-8").read()
    categorias = json.loads(categoria_data)
    films = topventas_database()
    novedades = []
    #Para cada pelicula añadimos a novedades un diccionario que contenga su id, para que lo acceda el template.
    #Recordamos que cada elemento de la lista resultado es una fila, y luego cada fila es una lista con las columnas.
    for p in films:

        pelicula = {}
        #Almacenamos el id de la película.
        pelicula['id'] =int(p[3])
        pelicula['title']=p[1]
        novedades.append(pelicula)

    if 'usuario' in session:
        usuario = session['usuario']
    else:
        usuario = None
    return render_template('index.html', title = "Pagina Principal", novedades = novedades, categorias= categorias['categorias'], session_usuario = usuario)

@app.route('/nusuarios')
@app.route('/articulodetalle/nusuarios')
def nusuarios():
    nusuarios = random.randrange(0, 2000, 1)
    return str(nusuarios)



def register_database(info):

    db_conn = None
    db_conn = db_engine.connect()
    register_query = f"INSERT INTO customers(username, password) VALUES ('{info['usuario']}', '{info['contrasena']}')"
    print(register_query)
    db_result = db_conn.execute(register_query)
    db_conn.close()


@app.route('/registro', methods=['GET', 'POST'])
def registro():

    if request.method == "GET":
        return render_template('registro.html', title = "Registro", alerta="" )

    elif request.method == "POST":

        info={}
        info['usuario']=request.form['usuario']
        info['genero']=request.form['genero']
        info['contrasena']=request.form['pwd1']
        info['email']=request.form['email']
        info['tarjeta']=request.form['tarjeta']
        info['tipotarjeta']=request.form['tipotarjeta']
        saldo = random.randrange(0, 101, 1)
        info['saldo']=str(saldo)

        register_database(info)


        return redirect(url_for('index'))


def login_database(username, password):
            # conexion a la base de datos
            try:
                db_conn = None
                db_conn = db_engine.connect()
                query_login = f"SELECT * FROM customers WHERE username = '{username}' and password = '{password}';"


                db_result = db_conn.execute(query_login)
                #Almacenamos el idusuario en el usuario.
                session['usuarioid'] = list(db_result)[0][0]

                db_conn.close()
                return  list(db_result)
            except:
                if db_conn is not None:
                    db_conn.close()
                return(None)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":




            password = request.form['lpwd']
            username = request.form['lusuario']


            result = login_database(username, password)
            if result is None:
                return render_template('login.html', title = "Sign In", alerta="Contraseña incorrecta.")
            else:
                session['usuario'] = request.form['lusuario']
                #session.modified=True
                resp = make_response(redirect(url_for('index')))
                resp.set_cookie('usuario', request.form['lusuario'])
                return resp



    elif request.method == "GET":
        usuario = request.cookies.get('usuario')
        # se puede guardar la pagina desde la que se invoca
        # session['url_origen']=request.referrer
        # session.modified=True
        # print a error.log de Apache si se ejecuta bajo mod_wsgi
        # print (request.referrer, file=sys.stderr)
        return render_template('login.html', title = "Sign In", alerta="", usuario = usuario)


@app.route('/resultado', methods=['GET', 'POST'])
def resultado():
    #Como si o si se selecciona categoria, si esta no está es porque quieren ver el formulario por primera vez, es GET.
    if 'categoria' in request.form:

        catalogue_data = open(os.path.join(app.root_path,'catalogue/catalogo.json'), encoding="utf-8").read()
        catalogue = json.loads(catalogue_data)
        resultados = []

        if 'usuario' in session:
            usuario = session['usuario']
        else:
            usuario = None

        if request.form['categoria'] == "--":

            if request.form['titulo'] == "":
                return redirect(url_for('index'))


            else:
                busqueda = request.form['titulo']
                for m in catalogue['peliculas']:
                    if m['titulo'] == request.form['titulo']:
                        resultados.append(m)
        else:
            if request.form['titulo'] == "":
                busqueda = request.form['categoria']
                for m in catalogue['peliculas']:
                    if m['categoria'] == request.form['categoria']:
                        resultados.append(m)
            else:
                busqueda = request.form['categoria'] + " y " +request.form['titulo']
                for m in catalogue['peliculas']:
                    if m['categoria'] == request.form['categoria'] and m['titulo'] == request.form['titulo']:
                        resultados.append(m)

        return render_template('resultado.html', title="Resultados", busqueda=busqueda, resultados = resultados, session_usuario = usuario)
    else:
        return redirect(url_for('index'))


@app.route('/historial', methods=['GET', 'POST'])
def historial(alert=""):
    if 'usuario' in session:
        usuario = session['usuario']
        if os.path.isfile(os.path.join(app.root_path,'usuarios/' + session['usuario'] + '/historial.json')):
            historial = json.load(open(os.path.join(app.root_path,'usuarios/' + session['usuario'] + '/historial.json'), 'r'))
            historial = historial['peliculas']
        else:
            historial = None
        if request.method == "POST":
            alert = "Su saldo ha sido actualizado correctamente"
            sumar_saldo(int(request.form['money']))

        saldo = obtener_saldo()[0]

    else:
        usuario = None
        historial = None
        saldo = None

    return render_template("historial.html", title="Historial de compras", peliculas=historial, session_usuario=usuario, alert=alert, saldo=saldo)


@app.route('/eliminarcarrito', methods=['GET', 'POST'])
def eliminarcarrito():
    print(request.form['id'])
    session['carrito'].remove(int(request.form['id']))

    return redirect(url_for('carrito'))


def anadircarrito_database(prod_id, quantity):

    db_conn = None
    db_conn = db_engine.connect()

    #Añadimos una nueva fila a orderdetail asociando nuestro carrito con el nuevo producto que acabamos de comprar,
    #teniendo en cuenta cuantos hemos comprado. Al tocar orderdetail, debería lanzarse nuestro trigger updOrders.
    query_articulodetalleprod = f"INSERT INTO orderdetail(orderid, prod_id, quantity) VALUES ({session['orderid']}, {prod_id}, {quantity})"
    db_result = db_conn.execute(query_articulodetalleprod)


    return


def comprarcarrito_database():

    db_conn = None
    db_conn = db_engine.connect()

    #Vamos a comprar nuestro carrito. Hemos de cambiar su status a PAID,
    # y por tanto nuestro trigger UpdInventory deberá actualizarse.
    query_articulodetalleprod = f"UPDATE orders SET status = 'Paid' WHERE orderid = {session['orderid']};"
    db_result = db_conn.execute(query_articulodetalleprod)


    return

def mostrarcarrito_database():

    db_conn = None
    db_conn = db_engine.connect()

    #Vamos a comprar nuestro carrito. Hemos de cambiar su status a PAID,
    # y por tanto nuestro trigger UpdInventory deberá actualizarse.
    query_articulodetalleprod = f"SELECT orderdetail.prod_id, orderdetail.quantity, imdb_movies.movietitle FROM orderdetail INNER JOIN products ON orderdetail.prod_id = products.prod_id INNER JOIN imdb_movies ON products.movieid = imdb_movies.movieid WHERE orderdetail.orderid = {session['orderid']}"
    db_result = db_conn.execute(query_articulodetalleprod)


    return list(db_result)

@app.route('/carrito', methods=['GET', 'POST'])
def carrito(alert = ""):
    total = 0.00
    peliscarrito=[]
    if 'orderid' in session.keys() and 'usuarioid' in session.keys():
        # catalogue_data = open(os.path.join(app.root_path,'catalogue/catalogo.json'), encoding="utf-8").read()
        # catalogue = json.loads(catalogue_data)

        #Comprobamos que es un post y además viendo que no tenemos ninguna alerta, ya que si no no sería querer Comprar
        #sino mostrar la pagina con el mensaje de error o aprobación
        if request.method == "POST" and alert == "":
            print("esjsdfj")
            comprarcarrito_database()

            session['carrito'].clear()
            #Queremos que nos muestre otra vez la página, pero esta vez con una alerta de error. Por tanto,
            #volvemos a llamar al view esta vez pasando la alerta.
            return carrito(alert)

        else:
            prodlist = mostrarcarrito_database()
            prodids = []
            for p in prodlist:
                e = {}
                e['quantity'] = p[1]
                e['prod_id'] = p[0]
                e['title'] = p[2]
                prodids.append(e)
    # if request.method == "POST" and alert == "":
    #
    #
    #
    #
    # if 'usuario' in session:
    #     usuario = session['usuario']
    # else:
    #
    #
    #
    #
    #     return
    usuario = session['usuario']
    return render_template("carrito.html", title="Carrito", peliculas=prodids, total=total, session_usuario=usuario, alert=alert)

def articulodetalle_database(movieid):

    try:
        db_conn = None
        db_conn = db_engine.connect()
        #Queremos mostrar un producto de la pelicula que acabamos de
        #recibir su id, por lo que hacemos la query y nos quedamos con el primero.

            #Cogemos el primer producto resultado asociado al movie_id:

        query_articulodetalleprod = f"SELECT imdb_movies.movietitle, imdb_movies.year, imdb_movies.movieid, products.prod_id FROM imdb_movies INNER JOIN products ON imdb_movies.movieid = products.movieid WHERE imdb_movies.movieid = '{movieid}';"
        db_result = db_conn.execute(query_articulodetalleprod)


        return list(db_result)[0]
    except:
        if db_conn is not None:
            db_conn.close()
        return(None)


def crearcarrito_database():
    #Si es la primera vez que compra y está logueado, añadimos el carrito a nuestra tabla order
    print("ADIOS")
    if 'usuario' in session:
        print("Ey")
        try:
            db_conn = None
            db_conn = db_engine.connect()
            print("Hola")
            print(session['usuarioid'])
            #En usuario id tenemos el idcostumer del usuario que está logueado.
            query_articulodetalleprod = f"INSERT INTO orders(customerid, orderdate) VALUES ({session['usuarioid']}, '2019-11-28');"

            db_result = db_conn.execute(query_articulodetalleprod)
            print("JAJAJAJA")
            #Ahora almacenamos en un campo de nuestra sesión el id del order para cuando queramos posteriormente acceder a él.
            query_articulodetalleprod = f"SELECT orderid FROM orders WHERE customerid = {session['usuarioid']} AND status is NULL;"
            db_result = db_conn.execute(query_articulodetalleprod)
            print("HOOSOSOSO")
            print(query_articulodetalleprod )
            session['orderid'] = list(db_result)[0][0]
            print(session['orderid'])
            return
        except:
            if db_conn is not None:
                db_conn.close()
            return(None)

@app.route('/articulodetalle/<peli_id>', methods=['GET', 'POST'])
def articulodetalle(peli_id):
    if 'usuario' in session:
        usuario = session['usuario']
    else:
        usuario = None

    alert = ""
    # catalogue_data = open(os.path.join(app.root_path,'catalogue/catalogo.json'), encoding="utf-8").read()
    # catalogue = json.loads(catalogue_data)
    #
    # for m in catalogue['peliculas']:
    #     if m['id'] == int(peli_id):

    movie = articulodetalle_database(peli_id)

    m = {}
    m['titulo'] = movie[0]
    m['estreno'] = movie[1]
    m['prod_id'] = movie[3]
    if request.method == "POST":
        #Mantenemos siempre ademas de en bbdd el carrito en la sesión.
        if not 'carrito' in session.keys():
            session['carrito'] = []
        #Si aún no hay entrada en orders de nuestro carrito y estamos logueados lo almacenamos.
        if not 'orderid' in session.keys() and 'usuarioid' in session.keys():
            crearcarrito_database()
        if(request.form['quantity'] == '1'):
            alert = "Su artículo ha sido añadido correctamente al carrito."
        else:
            alert = "Sus artículos han sido añadidos correctamente al carrito."

        for i in range(int(request.form['quantity'])):
            session['carrito'].append(m['prod_id'])
            anadircarrito_database(m['prod_id'], request.form['quantity'])

    return render_template('articulodetalle.html', title="Detalle de película", movie=m, alert=alert, session_usuario=usuario)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('usuario', None)
    session.pop('carrito', None)
    session.pop('historial', None)
    return redirect(url_for('index'))
