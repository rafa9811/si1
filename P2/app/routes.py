#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app
from flask import render_template, request, url_for, redirect, session
import json
import os
import sys
import crypt
import random
from hmac import compare_digest as compare_hash


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
    absdir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(absdir, "usuarios")
    path = os.path.join(path, session['usuario'])
    if os.path.isdir(path):
        #Necesitamos obtener el saldo del usuario almacenado
        ruta = path + "/datos.dat"
        f = open (ruta,'r')
        #Sabemos que el saldo está almacenado en la linea séptima
        f.readline()
        f.readline()
        f.readline()
        f.readline()
        f.readline()
        f.readline()
        #Lo primero es eliminar el newline de la string.
        linea = f.readline()
        #Después eliminamos el "contraseña: "
        saldo_usuario = float(linea.split(": ")[1])
        return saldo_usuario, ruta


def comprar(precio):
    saldo_usuario, ruta = obtener_saldo()
    if(precio > saldo_usuario):
        return "ERROR"
    else:
        saldo_usuario = saldo_usuario - precio
        actualizar_saldo(ruta, saldo_usuario)


def actualizar_saldo(path, saldo):
    f = open(path, "r")
    lineas = f.readlines()
    f.close()
    f = open(path, "w")
    for linea in lineas[:-1]:
        f.write(linea)
    f.write("Saldo inicial: " + str(saldo) + "\n")
    f.close()


def sumar_saldo(saldo):
    saldo_usuario, ruta = obtener_saldo()
    nuevo_saldo = saldo_usuario + float(saldo)
    actualizar_saldo(ruta, nuevo_saldo)


#Funciones de vista:
@app.route('/')
@app.route('/index')
def index():
    catalogue_data = open(os.path.join(app.root_path,'catalogue/catalogo.json'), encoding="utf-8").read()
    catalogue = json.loads(catalogue_data)
    novedades = []
    for m in catalogue['peliculas']:
        if m['novedad'] == 'Sí':
            novedades.append(m)
    categoria_data = open(os.path.join(app.root_path,'catalogue/categoria.json'), encoding="utf-8").read()
    categorias = json.loads(categoria_data)
    if 'usuario' in session:
        usuario = session['usuario']
    else:
        usuario = None
    return render_template('index.html', title = "Pagina Principal", novedades = novedades, categorias= categorias['categorias'], session_usuario = usuario)

@app.route('/nusuarios')
def nusuarios():
    nusuarios = random.randrange(0, 2000, 1)
    return str(nusuarios)

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == "GET":
        return render_template('registro.html', title = "Registro", alerta="" )

    elif request.method == "POST":
        #Creamos la carpeta del usuario que quiere registrarse.
        absdir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(absdir, "usuarios")
        path = os.path.join(path, request.form['usuario'])
        #Si el usuario ya está creado le informamos con alerta y mostramos otra vez el formulario.
        if os.path.isdir(path):
            return render_template('registro.html', title = "Registro", alerta="El usuario ya existe.")
        #Si no, lo creamos y almacenamos información.
        os.mkdir(path)
        #Creamos ahora el fichero datos.dat donde almacenaremos toda la información del usuario y tmb el historial.json
        #aunque aun no lo utilicemos.
        ruta = path + "/historial.json"
        f = open(ruta, 'w')
        f.close()

        ruta = path + "/datos.dat"
        f = open (ruta,'w')
        f.write("Nombre usuario: " + request.form['usuario'] + "\n")
        print(request.form['genero'])
        f.write("Género: " + request.form['genero'] + "\n")
        #Ahora encriptamos la contraseña antes de almacenarla.
        password = encryptMD5(request.form['pwd1'])
        f.write("Contraseña: " + password + "\n")
        f.write("Email: " + request.form['email'] + "\n")
        f.write("Tarjeta: " + request.form['tarjeta'] + "\n")
        f.write("Tipo de tarjeta: " + request.form['tipotarjeta'] + "\n")
        saldo = random.randrange(0, 101, 1)
        f.write("Saldo inicial: " + str(saldo) + "\n")
        f.close()
        return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        absdir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(absdir, "usuarios")
        path = os.path.join(path, request.form['lusuario'])
        if os.path.isdir(path):
            #Necesitamos obtener el hash de la contraseña del usuario almacenada
            ruta = path + "/datos.dat"
            f = open (ruta,'r')
            #Sabemos que la contraseña está almacenada en la linea tercera
            f.readline()
            f.readline()
            #Lo primero es eliminar el newline de la string.
            hash = f.readline()[:-1]
            #Después eliminamos el "contraseña: "
            hash = hash.split(": ")[1]
            #Si coinciden las contraseñas:
            if checkPassword(request.form["lpwd"], hash):
                session['usuario'] = request.form['lusuario']
                #session.modified=True
                return redirect(url_for('index'))

            else:
                return render_template('login.html', title = "Sign In", alerta="Contraseña incorrecta.")

        else:
            # aqui se le puede pasar como argumento un mensaje de login invalido
            return render_template('login.html', title = "Sign In", alerta="No existe usuario.")
    elif request.method == "GET":
        # se puede guardar la pagina desde la que se invoca
        # session['url_origen']=request.referrer
        # session.modified=True
        # print a error.log de Apache si se ejecuta bajo mod_wsgi
        # print (request.referrer, file=sys.stderr)
        return render_template('login.html', title = "Sign In", alerta="")


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
    else:
        usuario = None
        historial = None

    if request.method == "POST":
        alert = "Su saldo ha sido actualizado correctamente"
        sumar_saldo(int(request.form['money']))

    return render_template("historial.html", title="Historial de compras", peliculas=historial, session_usuario=usuario, alert=alert)


@app.route('/carrito', methods=['GET', 'POST'])
def carrito(alert=""):
    total = 0.00
    peliscarrito=[]
    if 'carrito' in session.keys():
        catalogue_data = open(os.path.join(app.root_path,'catalogue/catalogo.json'), encoding="utf-8").read()
        catalogue = json.loads(catalogue_data)

        #Comprobamos que es un post y además viendo que no tenemos ninguna alerta, ya que si no no sería querer Comprar
        #sino mostrar la pagina con el mensaje de error o aprobación.
        if request.method == "POST" and alert == "":
            peliculascompradas = {}
            peliculascompradas['peliculas'] = []
            for mid in session['carrito']:
                for movie in catalogue['peliculas']:
                    if movie['id'] == mid:
                        peliculascompradas['peliculas'].append(movie)
                        total += float(movie['precio'])

            if comprar(total)=="ERROR":
                alert = "No se ha podido realizar la compra por falta de saldo."
            else:
                alert = "Se ha efectuado correctamente la compra."

                if os.path.isfile(os.path.join(app.root_path,'usuarios/' + session['usuario'] + '/historial.json')):
                    file = open(os.path.join(app.root_path,'usuarios/' + session['usuario'] + '/historial.json'), 'r')
                    data = json.load(file)
                    file.close()

                else:
                    data = {}
                    data['peliculas'] = []

                for pelicula in peliculascompradas['peliculas']:
                    data['peliculas'].append(pelicula)

                with open(os.path.join(app.root_path,'usuarios/' + session['usuario'] + '/historial.json'), 'w') as file:
                    json.dump(data, file, indent=4)

                session['carrito'].clear()
            #Queremos que nos muestre otra vez la página, pero esta vez con una alerta de error. Por tanto,
            #volvemos a llamar al view esta vez pasando la alerta.
            return carrito(alert)

        else:
            for mid in session['carrito']:
                for movie in catalogue['peliculas']:
                    if movie['id'] == mid:
                        total += float(movie['precio'])
                        peliscarrito.append(movie)

    if 'usuario' in session:
        usuario = session['usuario']
    else:
        usuario = None

    return render_template("carrito.html", title="Carrito", peliculas=peliscarrito, total=total, session_usuario=usuario, alert=alert)


@app.route('/articulodetalle/<peli_id>', methods=['GET', 'POST'])
def articulodetalle(peli_id):
    catalogue_data = open(os.path.join(app.root_path,'catalogue/catalogo.json'), encoding="utf-8").read()
    catalogue = json.loads(catalogue_data)

    for m in catalogue['peliculas']:
        if m['id'] == int(peli_id):

            if request.method == "POST":
                if not 'carrito' in session.keys():
                    session['carrito'] = []
                for i in range(int(request.form['quantity'])):
                    session['carrito'].append(m['id'])

            return render_template('articulodetalle.html', title="Detalle de película", movie=m)
    return

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('usuario', None)
    session.pop('carrito', None)
    session.pop('historial', None)
    return redirect(url_for('index'))
