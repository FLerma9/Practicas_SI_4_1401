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
    carrito = []
    catalogue_data = open(os.path.join(app.root_path,'catalogue/catalogue.json'), encoding="utf-8").read()
    catalogue = json.loads(catalogue_data)

    peliculas = catalogue['peliculas']

    for pelicula in peliculas:
        if str(pelicula['id']) == "1" or "2":
            carrito.append(pelicula)

    if not carrito:
        return redirect(url_for('carrito'))

    return render_template('carrito.html', tittle='Carrito', carrito_movies=carrito)
