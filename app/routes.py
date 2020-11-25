#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app
from flask import render_template, request, url_for
from flask import redirect, session, make_response
from datetime import date
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
        categories.add(pelicula["categoria"])
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
        path_usuario = os.path.join(app.root_path, 'usuarios/' + str(username) + '/')
        path_dat = os.path.join(app.root_path, 'usuarios/' + str(username) + '/datos.dat')
        # Comprobamos que existe el usuario si existe su carpeta usuario
        if not os.path.exists(path_dat):
            msg = 'Error, no existe el usuario.'
            return render_template('login.html', title = "Sign In", msg = msg, user=user)
        datos = open(path_dat, 'r', encoding="utf-8")
        lines = datos.readlines()
        # Leemos los datos del fichero .dat
        username = lines[0].split(":")[1][:-1]
        salt = lines[1].split(":")[1][:-1]
        passwordDat = lines[2].split(":")[1][:-1]
        saldo = lines[5].split(":")[1][:-1]
        datos.close()
        if request.form['username'] == username:
            password = str(request.form['password'])
            pencrypted = hashlib.sha512((salt+password).encode('utf-8')).hexdigest()
            # Si el usuario y contraseña coinciden
            if pencrypted == passwordDat:
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
    comprueba que el usuario no exista previamente y se crean los directorios
    correspondientes con su .dat e historial.json. Es necesario hacer login
    después de registrarse.
    '''
    if 'username' in request.form:
        username = request.form['username']
        path_usuario = os.path.join(app.root_path,
                                    'usuarios/' + str(username) + '/')
        path_dat = os.path.join(app.root_path,
                                'usuarios/' + str(username) + '/datos.dat')
        path_json = os.path.join(app.root_path,
                                 'usuarios/' + str(username) + '/historial.json')
        #Creamos el directorio si no existe
        if os.path.exists(path_dat):
            msg = 'Error, el nombre de usuario ya existe'
            return render_template('register.html', title = "Register", msg = msg)
        else:
            try:
                os.mkdir(path_usuario)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    msg = 'Error creando directorio'
                    render_template('register.html', title = "Register", msg = msg)
                    raise
            datos = open(path_dat, 'w', encoding="utf-8")
            password = str(request.form['regPassword'])
            salt = hashlib.sha256(os.urandom(60)).hexdigest()
            pencrypted = hashlib.sha512((salt+password).encode('utf-8')).hexdigest()
            # Escribimos el usuario, contraseña, salt, email, tarjeta y saldo
            datos.write('username:' + str(username) + '\n')
            datos.write('salt:' + salt + '\n')
            datos.write('password:' + pencrypted + '\n')
            datos.write('email:' + str(request.form['email']) + '\n')
            datos.write('credit:' + str(request.form['credit']) + '\n')
            datos.write('saldo:' + str(random.randint(0, 100)) + '\n')
            datos.close()
            # Creamos el historial vacío.
            historial = open(path_json, 'w', encoding="utf-8")
            compras = {'compras':[]}
            json.dump(compras, historial)
            historial.close()
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

    indice = 0
    for peli in session['carrito']['Peliculas']:
        precio_peli =  ((session['carrito']['Peliculas'][indice]['cantidad']) * (session['carrito']['Peliculas'][indice]['precio']))
        # calculamos el precio de la suma de pelis del carrito
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

    catalogue_data = open(os.path.join(app.root_path,'catalogue/catalogue.json'), encoding="utf-8").read()
    catalogue = json.loads(catalogue_data)
    indice = 0
    action = 0
    precio_carrito = 0
    peliculas = catalogue['peliculas']

    if not 'usuario' in session:
        session['saldo'] = 0

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

    indice = 0
    # calculamos el precio total del carrito
    for peli in session['carrito']['Peliculas']:
        precio_peli =  ((session['carrito']['Peliculas'][indice]['cantidad']) * (session['carrito']['Peliculas'][indice]['precio']))
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
            if session['saldo'] > session['precio']: # si el saldo del usuario es mayor que el precio del carrito, se podra proceder a comprar, sino mostrara mensaje de saldo insuficiente
                cambiarSaldo(-session['precio'])
                historial_data = open(os.path.join(app.root_path,'usuarios/' + session['usuario'] + '/historial.json'), encoding="utf-8").read() #falta cambiar el path para cada usuario particular, esta con el modo prueba1
                hist = json.loads(historial_data) # abrimos el historial del usuario registrado

                if not hist['compras']: # miramos si tiene mas pedidos, para asignar numero de pedido
                    num_pedido = 1
                else:
                    for ped in hist['compras']:
                        num_pedido = ped['numero_pedido']
                    num_pedido = num_pedido + 1

                pedido_actual['numero_pedido'] = num_pedido
                pedido_actual['peliculas'] = []

                for pelicula in session['carrito']['Peliculas']: # actualizamos el historial del usuario
                    pedido_actual['peliculas'].append({'titulo': pelicula['titulo'], 'id': pelicula['id'], 'precio': pelicula['precio'], 'cantidad': pelicula['cantidad']})
                pedido_actual['fecha_pedido'] = current_date_format(fecha)
                pedido_actual['precio_total'] = round(float(session['precio']), 2)

                hist['compras'].append(pedido_actual)

                with open(os.path.join(app.root_path,'usuarios/' + session['usuario'] + '/historial.json'), 'w') as file: # escribimos en el historial.json del usuario
                    json.dump(hist, file)
                    session.pop('carrito') # esto es para que el carrito se vacie
                return render_template('historial.html', title = "Historial", historial=hist['compras'], saldo=session['saldo'])

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
        path_dat = os.path.join(app.root_path, 'usuarios/' + str(session['usuario']) + '/historial.json') #abrimos el historial.json del usuario para mostrarlo
        historial_data = open(path_dat, encoding="utf-8").read()
        session['historial'] = json.loads(historial_data)
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
    suma al saldo total de la session del usuario y que ademas se guarda
    en su .dat.
    '''
    if 'usuario' in session:
        saldo = session['saldo'] + int(cantidad)
        path_dat = os.path.join(app.root_path, 'usuarios/' + str(session['usuario']) + '/datos.dat')
        for line in fileinput.input(path_dat, inplace = 1):
            if 'saldo:' in line:
                line = line.replace(str(session['saldo']), str(saldo))
            sys.stdout.write(line)
        session['saldo'] = saldo

@app.route('/ajaxRandom', methods=['GET', 'POST'])
def ajaxRandom():
    '''
    Genera numeros aleatorios que concantena con una string para informar al
    cliente del numero de clientes.
    '''
    numero = random.randint(1, 100);
    cad = '<h5> Numero de usuarios conectados en este momento: ' + str(numero) + '</h5>'
    return cad

@app.route('/.wsgi/ajaxRandom', methods=['GET', 'POST'])
def ajaxRandom2():
    '''
    Genera numeros aleatorios que concantena con una string para informar al
    cliente del numero de clientes.
    '''
    numero = random.randint(1, 100);
    cad = '<h5> Numero de usuarios conectados en este momento: ' + str(numero) + '</h5>'
    return cad
