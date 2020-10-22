#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app
from flask import render_template, request, url_for, redirect, session
import json
import os
import sys

@app.route('/')
@app.route('/index')
def index():
    print (url_for('static', filename='estilo.css'), file=sys.stderr)
    catalogue_data = open(os.path.join(app.root_path,'catalogue/catalogue.json'), encoding="utf-8").read()
    catalogue = json.loads(catalogue_data)
    categories = set()
    for pelicula in catalogue['peliculas']:
        categories.add(pelicula["categoria"])
    session['saldo'] = 100
    print(session['saldo'])
    return render_template('index.html', title = "Home", movies=catalogue['peliculas'], categorias=categories)


@app.route('/search', methods=['POST',])
def search():
    catalogue_data = open(os.path.join(app.root_path,'catalogue/catalogue.json'), encoding="utf-8").read()
    catalogue = json.loads(catalogue_data)

    pelis_filtradas = filtrar(request.form['categoria'], catalogue['peliculas'])
    if request.form['busqueda'] != '':
        pelis_filtradas = busqueda_titulo(request.form['busqueda'], pelis_filtradas)

    categories = set()
    for pelicula in catalogue['peliculas']:
        categories.add(pelicula["categoria"])

    return render_template('index.html', title = "Home", movies=pelis_filtradas, categorias=categories)


def filtrar(category, peliculas):
    pelis_filtradas = []

    if category == "":
        return peliculas

    for pelicula in peliculas:
        if pelicula['categoria'] == category:
            pelis_filtradas.append(pelicula)

    return pelis_filtradas

def busqueda_titulo(titulo, peliculas):
    busqueda = []

    for pelicula in peliculas:
        if titulo in pelicula['titulo'] :
            busqueda.append(pelicula)

    return busqueda

@app.route('/login', methods=['GET', 'POST'])
def login():
    # doc sobre request object en http://flask.pocoo.org/docs/1.0/api/#incoming-request-data
    if 'username' in request.form:
        # aqui se deberia validar con fichero .dat del usuario
        if request.form['username'] == 'pp':
            session['usuario'] = request.form['username']
            session.modified=True
            # se puede usar request.referrer para volver a la pagina desde la que se hizo login
            return redirect(url_for('index'))
        else:
            # aqui se le puede pasar como argumento un mensaje de login invalido
            return render_template('login.html', title = "Sign In")
    else:
        # se puede guardar la pagina desde la que se invoca
        session['url_origen']=request.referrer
        session.modified=True
        # print a error.log de Apache si se ejecuta bajo mod_wsgi
        print (request.referrer, file=sys.stderr)
        return render_template('login.html', title = "Sign In")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'username' in request.form:
         #de momento lo dejamos
        return render_template('register.html', title = "Register")
    else:
        # se puede guardar la pagina desde la que se invoca
        session['url_origen']=request.referrer
        session.modified=True
        # print a error.log de Apache si se ejecuta bajo mod_wsgi
        print (request.referrer, file=sys.stderr)
        return render_template('register.html', title = "Register")

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('usuario', None)
    return redirect(url_for('index'))


@app.route('/details-<id>', methods=['GET', 'POST'])
def details(id):
    print (url_for('static', filename='estilo.css'), file=sys.stderr)
    pelicula_seleccionada = {}
    catalogue_data = open(os.path.join(app.root_path,'catalogue/catalogue.json'), encoding="utf-8").read()
    catalogue = json.loads(catalogue_data)

    peliculas = catalogue['peliculas']

    for pelicula in peliculas:
        if str(pelicula['id']) == id:
            pelicula_seleccionada = pelicula

    if not pelicula_seleccionada:
        return redirect(url_for('index'))


    return render_template('details.html', tittle='Details', movie=pelicula_seleccionada)


@app.route('/carrito', methods=['GET', 'POST'])
def carrito():
    print (url_for('static', filename='estilo.css'), file=sys.stderr)
    precio_carrito = 0


    if not 'carrito' in session:
        session['carrito'] = {'Peliculas':[]}
        session['precio'] = 0

    indice = 0
    for peli in session['carrito']['Peliculas']:
        precio_peli =  ((session['carrito']['Peliculas'][indice]['cantidad']) * (session['carrito']['Peliculas'][indice]['precio']))
        precio_carrito += precio_peli
        indice += 1
    session['precio'] = precio_carrito

    return render_template('carrito.html', tittle='Carrito', carrito_movies=session['carrito']['Peliculas'], precio = session['precio'], mensaje = '', Action = 0, saldo = session['saldo'])


@app.route('/add_carrito', methods=['GET', 'POST'])
def add_carrito():
    print (url_for('static', filename='estilo.css'), file=sys.stderr)
    id_pelicula = request.args.get('id_pelicula')

    catalogue_data = open(os.path.join(app.root_path,'catalogue/catalogue.json'), encoding="utf-8").read()
    catalogue = json.loads(catalogue_data)
    indice = 0
    action = 0
    precio_carrito = 0
    peliculas = catalogue['peliculas']

    if 'carrito' in session:
        for peli in session['carrito']['Peliculas']:
            if str(peli['id']) == id_pelicula:
                session['carrito']['Peliculas'][indice]['cantidad'] += 1
                action = 1
                break
            indice += 1
        if action == 0:
            indice = 0
            for pelicula in peliculas:
                if str(pelicula['id']) == id_pelicula:
                    session['carrito']['Peliculas'].append(pelicula)
            for peli in session['carrito']['Peliculas']:
                if str(peli['id']) == id_pelicula:
                    session['carrito']['Peliculas'][indice]['cantidad'] = 1
                indice += 1
    else:
        session['precio'] = 0
        session['carrito'] = {'Peliculas':[]}
        for pelicula in peliculas:
            if str(pelicula['id']) == id_pelicula:
                session['carrito']['Peliculas'].append(pelicula)
        for peli in session['carrito']['Peliculas']:
            if str(peli['id']) == id_pelicula:
                session['carrito']['Peliculas'][indice]['cantidad'] = 1
            indice += 1

    indice = 0
    for peli in session['carrito']['Peliculas']:
        precio_peli =  ((session['carrito']['Peliculas'][indice]['cantidad']) * (session['carrito']['Peliculas'][indice]['precio']))
        precio_carrito += precio_peli
        indice += 1
    session['precio'] = precio_carrito


    return render_template('carrito.html', tittle='Carrito', carrito_movies=session['carrito']['Peliculas'], precio = session['precio'], mensaje = '', Action = 0, saldo = session['saldo'])

@app.route('/remv_carrito', methods=['GET', 'POST'])
def remv_carrito():
    print (url_for('static', filename='estilo.css'), file=sys.stderr)
    id_pelicula = request.args.get('id_pelicula')
    precio_carrito = 0

    if 'carrito' in session:
        indice = 0
        for pelicula in session['carrito']['Peliculas']:
            if str(pelicula['id']) == id_pelicula:
                if session['carrito']['Peliculas'][indice]['cantidad'] > 1:
                    session['carrito']['Peliculas'][indice]['cantidad'] -= 1
                else:
                    session['carrito']['Peliculas'].remove(pelicula)
            indice += 1
    else:
        print("No existe carrito")

    indice = 0
    for peli in session['carrito']['Peliculas']:
        precio_peli =  ((session['carrito']['Peliculas'][indice]['cantidad']) * (session['carrito']['Peliculas'][indice]['precio']))
        precio_carrito += precio_peli
        indice += 1

    session['precio'] = precio_carrito


    return render_template('carrito.html', tittle='Carrito', carrito_movies=session['carrito']['Peliculas'], precio = session['precio'], mensaje = '', Action = 0, saldo = session['saldo'])

@app.route('/comp_carrito', methods= ['GET', 'POST'])
def comp_carrito():
    print (url_for('static', filename='estilo.css'), file=sys.stderr)
    session['usuario'] = 'jesus'  #esto es para probar
    precio_carrito = 0
    pedido_actual = {}
    action = 0
    mensaje = ""


    if session['carrito']['Peliculas']:
        if 'jesus' in session['usuario']:
            if session['saldo'] > session['precio']:
                session['saldo'] = session['saldo'] - session['precio']

                historial_data = open(os.path.join(app.root_path,'../usuarios/prueba1/historial.json'), encoding="utf-8").read() #falta cambiar el path para cada usuario particular, esta con el modo prueba1
                hist = json.loads(historial_data)

                for ped in hist['compras']:
                    num_pedido = ped['numero_pedido']

                num_pedido = num_pedido + 1
                pedido_actual['numero_pedido'] = num_pedido
                pedido_actual['peliculas'] = []

                for pelicula in session['carrito']['Peliculas']:
                    pedido_actual['peliculas'].append({'titulo': pelicula['titulo'], 'id': pelicula['id'], 'precio': pelicula['precio']})
                pedido_actual['fecha_pedido'] = "13" #falta la fecha
                pedido_actual['precio_total'] = session['precio']

                hist['compras'].append(pedido_actual)

                with open(os.path.join(app.root_path,'../usuarios/prueba1/historial.json'), 'w') as file: #aqui igual
                    json.dump(hist, file)
                return render_template('historial.html', title = "Historial", historial=hist['compras'])

            else:
                mensaje_carro = "No hay saldo suficiente"

        else:
            mensaje_carro = "Es necesario registrarse para esta funcionalidad"
            action = 1
    else:
        mensaje_carro = "No hay carrito"

    return render_template('carrito.html', tittle='Carrito', carrito_movies=session['carrito']['Peliculas'], precio = session['precio'], mensaje = mensaje_carro, Action = action, saldo = session['saldo'])

@app.route('/act_carrito', methods= ['GET', 'POST'])
def act_carrito():
    print (url_for('static', filename='estilo.css'), file=sys.stderr)
    id_pelicula = request.args.get('id_pelicula')
    cantidad = request.form.get("saldo")
    precio_carrito = 0

    if cantidad ==  "":
        indice = 0
        for peli in session['carrito']['Peliculas']:
            precio_peli =  ((session['carrito']['Peliculas'][indice]['cantidad']) * (session['carrito']['Peliculas'][indice]['precio']))
            precio_carrito += precio_peli
            indice += 1

        session['precio'] = precio_carrito

        return render_template('carrito.html', tittle='Carrito', carrito_movies=session['carrito']['Peliculas'], precio = session['precio'], mensaje = '', Action = 0, saldo = session['saldo'])



    catalogue_data = open(os.path.join(app.root_path,'catalogue/catalogue.json'), encoding="utf-8").read()
    catalogue = json.loads(catalogue_data)

    indice = 0
    for pelicula in session['carrito']['Peliculas']:
        if str(pelicula['id']) == id_pelicula:
            session['carrito']['Peliculas'][indice]['cantidad'] = int(cantidad)
        indice += 1

    indice = 0
    for peli in session['carrito']['Peliculas']:
        precio_peli =  ((session['carrito']['Peliculas'][indice]['cantidad']) * (session['carrito']['Peliculas'][indice]['precio']))
        precio_carrito += precio_peli
        indice += 1

    session['precio'] = precio_carrito


    return render_template('carrito.html', tittle='Carrito', carrito_movies=session['carrito']['Peliculas'], precio = session['precio'], mensaje = '', Action = 0, saldo = session['saldo'])

@app.route('/historial', methods=['GET', 'POST'])
def historial():
    historial_data = open(os.path.join(app.root_path,'../usuarios/prueba1/historial.json'), encoding="utf-8").read()
    historial = json.loads(historial_data)
    return render_template('historial.html', title = "Historial", historial=historial['compras'])
