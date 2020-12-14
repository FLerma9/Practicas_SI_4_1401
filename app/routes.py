#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app
from app import database
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
    # Obtenemos la tabla Top Ventas de la página principal.
    top = database.db_getTopVentas()
    for pelicula in catalogue['peliculas']:
        categories.add(pelicula["categoria"])
    return render_template('index.html', title="Home",
                           movies=catalogue['peliculas'],
                           categorias=categories, top=top)


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
        categories.add(pelicula["categoria"])

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
        if pelicula['categoria'] == category:
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
        if titulo in pelicula['titulo'] :
            busqueda.append(pelicula)

    return busqueda

@app.route('/login', methods=['GET', 'POST'])
def login():
    '''
    Funcion que se encarga de devolver la página del login si es una peticion
    GET o de procesar el formulario de login en el caso de que sea un POST.
    Si existe el usuario y coinciden las contraseñas se inicia la sesion con
    Flask Sessions y se redirige al index, si no coinciden o el usuario
    no existe se notifica el
    error mediante el html y se vuelve a cargar la pagina del login con el
    error.
    Tambíen crea la cookie que se envía al cliente para que la guarde y
    complete el campo input del username, con el ultimo usuario que ha logeado.
    '''
    user = request.cookies.get('username')
    # Si es POST
    if 'username' in request.form:
        username = request.form['username']
        # obtenemos la info del usuario de la BD
        data = database.db_getUserData(username)
        # si no hay coincidencia no hay usuario
        if len(data) == 0:
            msg = 'Error, no existe el usuario.'
            return render_template('login.html', title = "Sign In", msg = msg, user=user)

        # leemos la info de la BD
        username = data[0].username
        passwordDB = data[0].password
        saldo = data[0].income

        if request.form['username'] == username:
            password = str(request.form['password'])
            # Si el usuario y contraseña coinciden
            if password == passwordDB:
                # Iniciamos la session en FLask
                session['usuario'] = request.form['username']
                session['saldo'] = int(saldo)
                session.modified=True
                session.pop('historial', None)
                # Creamos la cookie
                resp = make_response(index())
                resp.set_cookie('username', username)
                return resp
            else:
                msg = 'Error contraseña incorrecta.'
                return render_template('login.html', title = "Sign In", msg = msg, user=user)
    # Si es GET
    else:
        # se puede guardar la pagina desde la que se invoca
        session['url_origen']=request.referrer
        session.modified=True
        # print a error.log de Apache si se ejecuta bajo mod_wsgi
        print (request.referrer, file=sys.stderr)
        return render_template('login.html', title = "Sign In", msg = None, user=user)


@app.route('/register', methods=['GET', 'POST'])
def register():
    '''
    Si la peticion es GET se devuelve el html con el formulario de registro.
    Si es POST y ya se ha valido con JS los campos del formulario, se
    comprueba que el usuario no exista previamente y se crea en la BD.
    Es necesario hacer login después de registrarse.
    '''
    if 'username' in request.form:
        username = request.form['username']
        # obtenemos la info del usuario de la BD
        data = database.db_getUserData(username)
        # si hay coincidencia no puede crear el usuario
        if len(data) == 1:
            msg = 'Error, el nombre de usuario ya existe'
            return render_template('register.html', title = "Register", msg = msg)
        else:
            password = str(request.form['regPassword'])
            username = str(username)
            email = str(request.form['email'])
            credit = str(request.form['credit'])
            income = str(random.randint(0, 100))
            database.db_createCustomer(username, password, email, credit, income)
            msg = 'Usuario creado correctamente, inicie sesion.'
            return render_template('register.html', title = "Register", msg = msg)
    else:
        # se puede guardar la pagina desde la que se invoca
        session['url_origen']=request.referrer
        session.modified=True
        # print a error.log de Apache si se ejecuta bajo mod_wsgi
        print (request.referrer, file=sys.stderr)
        return render_template('register.html', title = "Register", msg = None)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    '''
    Libera todo lo guardado en la session y redirige al usuario al index
    pero ahora de manera anonima.
    '''
    session.pop('usuario', None)
    session.pop('carrito', None)
    session.pop('historial', None)
    session.pop('saldo', None)
    session.pop('precio', None)
    return redirect(url_for('index'))


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
    catalogue_data = open(os.path.join(app.root_path,'catalogue/catalogue.json'), encoding="utf-8").read()
    catalogue = json.loads(catalogue_data)

    peliculas = catalogue['peliculas']

    # Cogemos la peli por id
    for pelicula in peliculas:
        if str(pelicula['id']) == id:
            pelicula_seleccionada = pelicula

    # Si no hay pelicula con el id se devuelve index
    if not pelicula_seleccionada:
        return redirect(url_for('index'))


    return render_template('details.html', tittle='Details',
                           movie=pelicula_seleccionada)


@app.route('/carrito', methods=['GET', 'POST'])
def carrito():
    '''
    Devuelve el html que carga en el cliente la página con el carrito del
    cliente.
    '''
    print (url_for('static', filename='css/estilo.css'), file=sys.stderr)
    precio_carrito = 0

    if not 'usuario' in session:
        session['saldo'] = 0
    # si no existe una sesion de carrito creamos el diccionario vacio
    if not 'carrito' in session:
        session['carrito'] = {'Peliculas':[]}
        session['precio'] = 0

    if 'usuario' in session:
        id_pedido = database.get_id_pedido(session['usuario'])
        print(id_pedido)

        if id_pedido:
            session['carrito'] = database.getCarrito(id_pedido)
            session['precio'] = database.getPrecio(id_pedido)
        else:
            if not session['carrito']['Peliculas']:
                print("yep")
                database.newOrder(session['usuario'], [])
                id_pedido = database.get_id_pedido(session['usuario'])
                session['carrito'] = database.getCarrito(id_pedido)
                session['precio'] = database.getPrecio(id_pedido)
            else:
                print('yip')
                database.newOrder(session['usuario'], session['carrito']['Peliculas'])
                id_pedido = database.get_id_pedido(session['usuario'])
                session['carrito'] = database.getCarrito(id_pedido)
                session['precio'] = database.getPrecio(id_pedido)

    if not 'usuario' in session:
        indice = 0
        for peli in session['carrito']['Peliculas']:
            precio_peli =  ((session['carrito']['Peliculas'][indice]['cantidad']) * (session['carrito']['Peliculas'][indice]['precio']))
             #calculamos el precio de la suma de pelis del carrito
            precio_carrito += precio_peli
            indice += 1
        session['precio'] = round(float(precio_carrito), 2)


    session.modified=True
    return render_template('carrito.html', tittle='Carrito',
                           carrito_movies=session['carrito']['Peliculas'],
                           precio = session['precio'], mensaje = '',
                           Action = 0, saldo = session['saldo'])


@app.route('/add_carrito', methods=['GET', 'POST'])
def add_carrito():
    '''
    Añade al carrito del usuario o el anonimo la pelicula seleccionada,
    de manera que al añadir nos redirige a la pagina del carrito donde
    podremos ver el nuevo elemento añadido.
    '''
    print (url_for('static', filename='css/estilo.css'), file=sys.stderr)
    # recogemos el id de la pelicula cuya cantidad va a ser anadida
    id_pelicula = request.args.get('id_pelicula')
    print('ooooooo')
    print(id_pelicula)



    catalogue_data = open(os.path.join(app.root_path,'catalogue/catalogue.json'), encoding="utf-8").read()
    catalogue = json.loads(catalogue_data)
    indice = 0
    action = 0
    precio_carrito = 0
    peliculas = catalogue['peliculas']

    if not 'usuario' in session:
        session['saldo'] = 0

    if not 'usuario' in session:
        if 'carrito' in session:
            for peli in session['carrito']['Peliculas']:
                if str(peli['id']) == id_pelicula:
                    # actualizamos la cantidad de la pelicula en el carrito
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
            # creamos un nuevo carrito al que anadiremos primera pelicula
            session['carrito'] = {'Peliculas':[]}
            for pelicula in peliculas:
                if str(pelicula['id']) == id_pelicula:
                    session['carrito']['Peliculas'].append(pelicula)
            for peli in session['carrito']['Peliculas']:
                if str(peli['id']) == id_pelicula:
                    # actualizamos la cantidad de esa pelicula a 1
                    session['carrito']['Peliculas'][indice]['cantidad'] = 1
                indice += 1
    else:
        id_pedido = database.get_id_pedido(session['usuario'])
        print('***********')
        print(id_pedido)
        print('***********')

        if id_pedido:
            if database.peli_in_order(id_pelicula, id_pedido):
                database.add_peli(id_pelicula, id_pedido)
                session['carrito'] = database.getCarrito(id_pedido)
                session['precio'] = database.getPrecio(id_pedido)

            else:
                print(id_pelicula)
                database.create_peli(id_pelicula, id_pedido)
                session['carrito'] = database.getCarrito(id_pedido)
                session['precio'] = database.getPrecio(id_pedido)
        else:
            print("kkkk")
            database.newOrder(session['usuario'], [])
            id_pedido = database.get_id_pedido(session['usuario'])
            database.create_peli(id_pelicula, id_pedido)
            session['carrito'] = database.getCarrito(id_pedido)
            session['precio'] = database.getPrecio(id_pedido)

    print(session['carrito']['Peliculas'])


    if not 'usuario' in session:
        indice = 0
        for peli in session['carrito']['Peliculas']:
            precio_peli =  ((session['carrito']['Peliculas'][indice]['cantidad']) * (session['carrito']['Peliculas'][indice]['precio']))
             #calculamos el precio de la suma de pelis del carrito
            precio_carrito += precio_peli
            indice += 1
        session['precio'] = round(float(precio_carrito), 2)

    session.modified=True
    return render_template('carrito.html', tittle='Carrito',
                           carrito_movies=session['carrito']['Peliculas'],
                           precio = session['precio'],
                           mensaje = '', Action = 0, saldo = session['saldo'])

@app.route('/remv_carrito', methods=['GET', 'POST'])
def remv_carrito():
    '''
    Elimina del carrito de la session el elemento seleccionado, al terminar
    nos redirige al carrito donde se puede comprobar que ya no existe.
    '''
    print (url_for('static', filename='css/estilo.css'), file=sys.stderr)
    id_pelicula = request.args.get('id_pelicula')
    precio_carrito = 0

    if not 'usuario' in session:
        session['saldo'] = 0

    if not 'usuario' in session:
        if 'carrito' in session:
            indice = 0
            for pelicula in session['carrito']['Peliculas']:
                if str(pelicula['id']) == id_pelicula: # comprobamos que la cantidad de la pelicula que queremos anadir es mayor que uno y le restamos una unidad
                    if session['carrito']['Peliculas'][indice]['cantidad'] > 1:
                        session['carrito']['Peliculas'][indice]['cantidad'] -= 1
                    else:
                        # si la cantidad es uno eliminamos la pelicula del carrito
                        session['carrito']['Peliculas'].remove(pelicula)
                indice += 1
        else:
            print("No existe carrito")
    else:
        id_pedido = database.get_id_pedido(session['usuario'])
        print(id_pelicula)
        database.rmv_pelicula(id_pelicula, id_pedido)
        session['carrito'] = database.getCarrito(id_pedido)
        session['precio'] = database.getPrecio(id_pedido)
        print(session['precio'])
        if session['carrito']['Peliculas'] == {}:
            mensaje = 'Carrito vacio'

    if not 'usuario' in session:
        indice = 0
        # calculamos el precio del carrito como en otras funciones
        for peli in session['carrito']['Peliculas']:
            precio_peli =  ((session['carrito']['Peliculas'][indice]['cantidad']) * (session['carrito']['Peliculas'][indice]['precio']))
            precio_carrito += precio_peli
            indice += 1
        session['precio'] = round(float(precio_carrito), 2)


    session.modified=True
    return render_template('carrito.html', tittle='Carrito', carrito_movies=session['carrito']['Peliculas'], precio = session['precio'], mensaje = '', Action = 0, saldo = session['saldo'])

def current_date_format(date):
    '''
    Funcion auxiliar al que se la pasa un objeto de tipo date y nos
    devuelve un string de la forma que mostraremos la fecha en el hidtorial.
    '''
    months = ("Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio",
              "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre")
    day = date.day
    month = months[date.month - 1]
    year = date.year
    messsage = "{} de {} del {}".format(day, month, year)

    return messsage

@app.route('/comp_carrito', methods= ['GET', 'POST'])
def comp_carrito():
    '''
    Funcion para proceder a comprar el carrito, si el usuario no esta
    registrado no lo podra comprar, y se le pedira que inicie sesion o se
    registre. Si no tiene suficiente saldo tampoco lo podra comprar y
    se le notificara. Si tiene saldo suficiente, se crea un nuevo pedido
    en el historial del usuario y se le resta del saldo la cantidad.
    '''
    print (url_for('static', filename='css/estilo.css'), file=sys.stderr)
    precio_carrito = 0
    pedido_actual = {}
    fecha = date.today()
    action = 0
    mensaje = ""
    session.modified=True

    if not 'usuario' in session:
        session['saldo'] = 0

    if session['carrito']['Peliculas']: # si existe carrito se podra proceder a la compra, sino se mostrara un mensaje de carrito vacio
        if 'usuario' in session: # si el usuario esta registrado y se encuentra en sesion activa dejara proceder a intentar comprar, sino se mostrara un mensaje para redirigir a la pagina de registrar
            id_pedido = database.get_id_pedido(session['usuario'])
            if not database.not_exist_stock(id_pedido):
                print(session['saldo'])
                if session['saldo'] > session['precio']: # si el saldo del usuario es mayor que el precio del carrito, se podra proceder a comprar, sino mostrara mensaje de saldo insuficiente
                    cambiarSaldo(-session['precio'])
                    session['saldo'] = session['saldo'] - session['precio']
                    database.pagar_pedido(id_pedido)
                    session.pop('carrito') # esto es para que el carrito se vacie
                    id_usuario = database.get_id_usuario(session['usuario'])
                    session['historial'] = {'compras': []}
                    print(id_usuario)
                    session['historial']['compras'] = database.getHistorial(id_usuario)
                    return render_template('historial.html', title = "Historial", historial=session['historial']['compras'], saldo=session['saldo'])

                else:
                    mensaje_carro = "No hay saldo suficiente"
            else:
                print("LOLLLLLLL")
                mensaje_carro = "No hay suficiente stock para "+database.not_exist_stock(id_pedido)+". Contacta con atencion al cliente."

        else:
            mensaje_carro = "Es necesario registrarse para esta funcionalidad"
            action = 1
    else:
        mensaje_carro = "No hay carrito"

    return render_template('carrito.html', tittle='Carrito', carrito_movies=session['carrito']['Peliculas'], precio = session['precio'], mensaje = mensaje_carro, Action = action, saldo = session['saldo'])

@app.route('/act_carrito', methods= ['GET', 'POST'])
def act_carrito():
    '''
    Funcion para actualizar la cantidad de una pelicula del carrito.
    '''
    print (url_for('static', filename='css/estilo.css'), file=sys.stderr)
    id_pelicula = request.args.get('id_pelicula')
    cantidad = request.form.get("saldo") # guardamos la cantidad que se quiere actualizar de la pelicula, introducida a traves del imput
    precio_carrito = 0
    session.modified=True

    if not 'usuario' in session:
        session['saldo'] = 0

    if cantidad ==  "":
        indice = 0
        for peli in session['carrito']['Peliculas']:
            precio_peli =  ((session['carrito']['Peliculas'][indice]['cantidad']) * (session['carrito']['Peliculas'][indice]['precio']))
            precio_carrito += precio_peli
            indice += 1

        session['precio'] = precio_carrito

        return render_template('carrito.html', tittle='Carrito',
                               carrito_movies=session['carrito']['Peliculas'],
                               precio = session['precio'], mensaje = '',
                               Action = 0, saldo = session['saldo'])



    catalogue_data = open(os.path.join(app.root_path,'catalogue/catalogue.json'), encoding="utf-8").read()
    catalogue = json.loads(catalogue_data)

    if not 'usuario' in session:
        indice = 0
        for pelicula in session['carrito']['Peliculas']:
            if str(pelicula['id']) == id_pelicula:
                session['carrito']['Peliculas'][indice]['cantidad'] = int(cantidad) # actualizamos la cantidad de esa pelicula
            indice += 1

        indice = 0
        for peli in session['carrito']['Peliculas']: # recalculamos el nuevo precio del carrito
            precio_peli =  ((session['carrito']['Peliculas'][indice]['cantidad']) * (session['carrito']['Peliculas'][indice]['precio']))
            precio_carrito += precio_peli
            indice += 1
        session['precio'] = round(float(precio_carrito), 2)
    else:
        id_pedido = database.get_id_pedido(session['usuario'])
        database.act_pelicula(id_pelicula, id_pedido, cantidad)
        session['carrito'] = database.getCarrito(id_pedido)
        session['precio'] = database.getPrecio(id_pedido)





    return render_template('carrito.html', tittle='Carrito',
                            carrito_movies=session['carrito']['Peliculas'],
                            precio = session['precio'], mensaje = '',
                            Action = 0, saldo = session['saldo'])

@app.route('/historial', methods=['GET', 'POST'])
def historial():
    '''
    Funcion para mostrar el historial de un usuario.
    '''
    saldo = None
    session['historial'] = {'compras': []}
    action = 0
    if 'usuario' in session:
        id_usuario = database.get_id_usuario(session['usuario'])
        print(id_usuario)
        session['historial']['compras'] = database.getHistorial(id_usuario)
        print(session['historial'])
        saldo = session['saldo']
        action = 1
    return render_template('historial.html', title = "Historial",
                           historial=session['historial']['compras'],
                           saldo=saldo, action = action,
                           mensaje = 'Registrese para disfrutar de esta funcionalidad')


@app.route('/add_saldo', methods=['POST',])
def add_saldo():
    '''
    Función dinámica que permite al usuario logeado que añada saldo a su
    cuenta y que se guarde correctamente en su fichero .dat y session.
    '''
    if request.form['saldo']:
        if int(request.form['saldo']) > 0:
            cambiarSaldo(request.form['saldo'])
    return redirect(url_for('historial'))

def cambiarSaldo(cantidad):
    '''
    Funcion que recibe una cantidad entera positiva o negativa, que se le
    suma al saldo total de la session del usuario y lo actualiza en la BD.
    '''
    if 'usuario' in session:
        saldo = session['saldo'] + int(cantidad)
        session['saldo'] = saldo
        database.db_actualizarIncome(saldo, session['usuario'])

@app.route('/ajaxRandom', methods=['GET', 'POST'])
def ajaxRandom():
    '''
    Genera numeros aleatorios que concantena con una string para informar al
    cliente del numero de clientes.
    '''
    numero = random.randint(1, 100);
    cad = '<h5> Numero de usuarios conectados en este momento: ' + str(numero) + '</h5>'
    return cad

@app.route('/topUSA', methods=['GET',])
def topUSA():
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
