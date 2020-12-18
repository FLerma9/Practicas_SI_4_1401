#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app
from flask import render_template, request, url_for
from flask import redirect, session, make_response
from datetime import date
from pymongo import MongoClient
import json
import os
import errno
import sys
import random
import hashlib
import fileinput


@app.route('/')
@app.route('/index')
def index():
    '''
    View para la url /index y /. Obtiene el catalogo de peliculas al partir del
    json y carga los datos en el html index.html, el cual devuelve al cliente.
    '''
    print(url_for('static', filename='css/estilo.css'), file=sys.stderr)
    catalogue_data = open(os.path.join(app.root_path, 'catalogue/catalogue.json'), encoding="utf-8").read()
    catalogue = json.loads(catalogue_data)  # cargamos el catalogo
    categories = set()
    for pelicula in catalogue['peliculas']:
        for categoria in pelicula["genres"]:
            categories.add(categoria)
    return render_template('index.html', title="Home",
                           movies=catalogue['peliculas'],
                           categorias=categories)


@app.route('/search', methods=['POST',])
def search():
    '''
    View para la url /search. Los parámetros de la búsqueda, ya sea el
    filtrado o la busqueda, se pasan dentro de una peticion POST.
    Obtiene del catálogo las peliculas y las filtra por categoría, y
    después realiza una búsqueda por los titulos.
    Devuelve la pagina principal, pero solo con las peliculas que cumplen
    el filtrado y la busqueda.
    '''
    catalogue_data = open(os.path.join(app.root_path,'catalogue/catalogue.json'), encoding="utf-8").read()
    catalogue = json.loads(catalogue_data)

    #Filtramos por categoría
    pelis_filtradas = filtrar(request.form['categoria'], catalogue['peliculas'])
    #Si hay una string de busqueda, la realizamos
    if request.form['busqueda'] != '':
        pelis_filtradas = busqueda_titulo(request.form['busqueda'], pelis_filtradas)

    categories = set()
    for pelicula in catalogue['peliculas']:
        for categoria in pelicula["genres"]:
            categories.add(categoria)

    return render_template('index.html', title = "Home",
                           movies=pelis_filtradas, categorias=categories)

def filtrar(category, peliculas):
    '''
    args: category <- String con la categoría para filtrar, puede ser la vacía
          peliculas <- diccionario con las peliculas

    Devuelve una lista con las peliculas que cumplen la categoria, si no hay
    categoria devuelve todas las peliculas.
    '''
    pelis_filtradas = []
    #Si no hay categoria, devolvemos todas las pelis ya que no se filtra
    if category == "":
        return peliculas

    for pelicula in peliculas:
        for genre in pelicula["genres"]:
            if genre == category:
                pelis_filtradas.append(pelicula)
    return pelis_filtradas

def busqueda_titulo(titulo, peliculas):
    '''
    args: titulo <- String para la busqueda en el titulo.
          peliculas <- diccionario con las peliculas

    Devuelve una lista con las peliculas que contienen en el titulo
    la string de busqueda.
    '''
    busqueda = []

    for pelicula in peliculas:
        if titulo in pelicula['title'] :
            busqueda.append(pelicula)
    return busqueda


@app.route('/details-<id>', methods=['GET', 'POST'])
def details(id):
    '''
    Se pasa como argumennto el id de la pelicula con
    lo que se creara el url para los detalles de cada una.
    Devuelve el documento HTML con los detalles de la pelicula seleccionada.
    '''
    print (url_for('static', filename='css/estilo.css'), file=sys.stderr)
    pelicula_seleccionada = {}
    # cogemos el catalog del json
    myclient = MongoClient("mongodb://localhost:27017/")
    mydb = myclient["si1"]
    mycol = mydb["topUSA"]
    print(id)
    for x in mycol.find({"_id": int(id)}):
        pelicula_seleccionada = x

    # Si no hay pelicula con el id se devuelve index
    if not pelicula_seleccionada:
        return redirect(url_for('index'))


    return render_template('details.html', tittle='Details',
                           movie=pelicula_seleccionada)


@app.route('/topUSA', methods=['GET',])
def topUSA():
    '''
    Función que realiza las 3 consultas en la base de datos de MongoDB a traves
    de pymongo. Las consultas se explican en la memoria. El resultado de las
    consultas se pasa al html para renderizar las tablas.
    '''
    myclient = MongoClient("mongodb://localhost:27017/")
    mydb = myclient["si1"]
    mycol = mydb["topUSA"]
    consulta1 = []
    for x in mycol.find({"$and":[
                                 {"title" : {"$regex" : ".*Life.*"}},
                                 { "genres": { "$in": ["Comedy"] } },
                                 {"year" : {"$regex" : ".*1997.*"}}]}).sort("title").sort("Year"):
        consulta1.append(x)
    consulta2 = []
    for x in mycol.find({"$and":[
                                 { "directors": { "$in": ['Allen, Woody']}},
                                 {"year" : {"$regex" : ".*199[0-9].*"}}]}).sort("title").sort("Year"):
        consulta2.append(x)
    consulta3 = []
    for x in mycol.find({ "actors": { "$all": [ "Galecki, Johnny", "Parsons, Jim (II)"] } }).sort("title").sort("Year"):
        consulta3.append(x)
    consultas = []
    consultas.append(consulta1)
    consultas.append(consulta2)
    consultas.append(consulta3)
    return render_template('topusa.html', title = 'Top USA', consultas=consultas)
