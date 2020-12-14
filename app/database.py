import os
import sys, traceback
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, text
from sqlalchemy.sql import select
from sqlalchemy import func

# configurar el motor de sqlalchemy
db_engine = create_engine("postgresql://alumnodb:alumnodb@localhost/si1", echo=False)
db_meta = MetaData(bind=db_engine)
# cargar una tabla
db_table_orders = Table('orders', db_meta, autoload=True, autoload_with=db_engine)
db_table_orderdetail = Table('orderdetail', db_meta, autoload=True, autoload_with=db_engine)

def db_error(db_conn):
    '''
    Busca en la BD el usuario, contraseña y saldo a partir del username
    que nos dan en el login. Devolvemos el resultado de la query de abajo.
    '''
    if db_conn is not None:
        db_conn.close()
    print("Exception in DB access:")
    print("-"*60)
    traceback.print_exc(file=sys.stderr)
    print("-"*60)
    return 'Something is broken'

def get_id_pedido(user):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        # Sacar el id del pedido si el usuario tiene alguno
        db_result = db_conn.execute("Select orderid from orders as o, customers as c where c.customerid = o.customerid and c.username ='"+user+"' and o.status is null")

        result = list(db_result)

        if len(result)==0:
            db_conn.close()
            return False
        db_conn.close()

        return result[0][0]

    except:
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return 'Something is broken'

def getCarrito(pedido):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        # Sacar las peliculas del pedido del usuario
        db_result = db_conn.execute("Select prod_id, price, quantity from orders as o, orderdetail as od where o.orderid = '" +str(pedido)+ "' and o.orderid = od.orderid")
        order = list(db_result)
        order_final = []
        for o in order:
            db_result1 = db_conn.execute("Select movietitle from imdb_movies as m, products as p where p.prod_id = '" +str(o[0])+"' and p.movieid = m.movieid")
            title = list(db_result1)
            order_final.append({"id": o[0], "titulo": title[0][0], "precio": float(o[1]), "cantidad": int(o[2])})
        resultado = {'Peliculas': order_final}
        db_conn.close()

        return resultado
    except:
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return 'Something is broken'
def getPrecio(pedido):
    try:

    # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        # Sacar el id del pedido si el usuario tiene alguno
        db_result = db_conn.execute("Select totalamount from orders as o where o.orderid = '" +str(pedido)+ "'")

        db_conn.close()
        result = list(db_result)

        if len(result)==0 or result[0][0] == None:
            db_conn.close()
            return float(0)

        return float(result[0][0])
    except:

        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return 'Something is broken'


def newOrder(user, pedido):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()


        db_result = db_conn.execute("Select customerid from customers where username = '" +str(user)+ "'")
        usuario = list(db_result)
        # Sacar el id del pedido si el usuario tiene alguno

        db_conn.execute("insert into orders (orderdate, customerid, tax, status) values(NOW(), '"+str(usuario[0][0])+"', 15, null)")

        if pedido:
            db_result1 = db_conn.execute("Select orderid from orders where customerid = '" +str(usuario[0][0])+ "' and status is null")
            id_order = list(db_result1)

            for p in pedido:
                db_conn.execute("insert into orderdetail (orderid, prod_id, price, quantity) values('"+str(id_order[0][0])+"', '"+str(p['id'])+"', '"+str(p['precio'])+"', '"+str(p['cantidad'])+"')")


        db_conn.close()
        return True

    except:
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return 'Something is broken'

def peli_in_order(idproducto, pedido):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        # Sacar el id del pedido si el usuario tiene alguno
        db_result = db_conn.execute("Select prod_id from orders as o, orderdetail as od where o.orderid = '" +str(pedido)+ "' and o.orderid = od.orderid")
        order = list(db_result)
        for o in order:
            if int(o[0]) == idproducto:
                db_conn.close()
                return True

        db_conn.close()
        return False

    except:
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return 'Something is broken'

def create_peli(idproducto, pedido):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        # Sacar el id del pedido si el usuario tiene alguno
        db_result = db_conn.execute("Select price from products as p where p.prod_id = '" +str(idproducto)+ "'")
        peli = list(db_result)

        db_conn.execute("insert into orderdetail values("+str(pedido)+", "+str(idproducto)+", " +str(peli[0][0])+", 1)")

        db_conn.close()
        return True
    except:
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return 'Something is broken'

def add_peli(idproducto, pedido):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        # Sacar el id del pedido si el usuario tiene alguno
        db_result1 = db_conn.execute("Select quantity from orderdetail as od where od.orderid = '" +str(pedido)+ "' and od.prod_id = '" +str(idproducto)+"'")
        cantidad = list(db_result1)

        cantidadfinal = cantidad[0][0] + 1
        db_conn.execute("update orderdetail set quantity = '" +str(cantidadfinal)+"' where orderid = '" +str(pedido)+ "' and prod_id = '" +str(idproducto)+"'")

        db_conn.close()
        return True

    except:
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return 'Something is broken'

def rmv_pelicula(idproducto, pedido):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        # Sacar el id del pedido si el usuario tiene alguno

        db_result1 = db_conn.execute("Select quantity from orderdetail as od where od.orderid = '" +str(pedido)+ "' and od.prod_id = '" +str(idproducto)+"'")
        cantidad = list(db_result1)

        if cantidad[0][0] > 1:
            cantidadfinal = cantidad[0][0] - 1
            db_conn.execute("update orderdetail set quantity = '" +str(cantidadfinal)+"' where orderid = '" +str(pedido)+ "' and prod_id = '" +str(idproducto)+"'")
        else:
            db_conn.execute("delete from orderdetail where orderid = '" +str(pedido)+ "' and prod_id = '" +str(idproducto)+"'")


        db_conn.close()
        return True

    except:
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return 'Something is broken'

def act_pelicula(idproducto, pedido, cantidad1):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        # Sacar el id del pedido si el usuario tiene alguno
        db_result1 = db_conn.execute("Select quantity from orderdetail as od where od.orderid = '" +str(pedido)+ "' and od.prod_id = '" +str(idproducto)+"'")
        cantidad = list(db_result1)

        cantidadfinal = cantidad1
        db_conn.execute("update orderdetail set quantity = '" +str(cantidadfinal)+"' where orderid = '" +str(pedido)+ "' and prod_id = '" +str(idproducto)+"'")

        db_conn.close()
        return True

    except:
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return 'Something is broken'

def not_exist_stock(pedido):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        db_result = db_conn.execute("Select prod_id from orderdetail as od where od.orderid = '" +str(pedido)+ "' ")
        carrito = list(db_result)
        print(carrito)

        for p in carrito:
            db_result1 = db_conn.execute("Select quantity from orderdetail as od where od.orderid = '" +str(pedido)+ "' and od.prod_id = '" +str(p[0])+"'")
            cantidad = list(db_result1)
            db_result2 = db_conn.execute("Select stock from inventory as i where i.prod_id = '" +str(p[0])+"'")
            stock = list(db_result2)
            if cantidad[0][0] > stock[0][0]:
                db_result3 = db_conn.execute("Select movietitle from products as p, imdb_movies as m where p.prod_id = '" +str(p[0])+"' and p.movieid = m.movieid")
                producto_agotado = list(db_result3)
                print(producto_agotado[0][0])

                return producto_agotado[0][0]

        return False


    except:
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return 'Something is broken'

def pagar_pedido(pedido):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        db_conn.execute("Update orders set status = 'Paid' where orderid = '" +str(pedido)+"'")

        return True


    except:
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return 'Something is broken'


def db_getTopVentas():
    '''
    Realiza la funcion getTopVentas con los últimos 6 años de manera que nos
    devuelve 6 peliculas, siendo las mas vendidas de cada año.
    Se llama cada vez que se carga index.
    '''
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()
        db_result = db_conn.execute("SELECT * FROM getTopVentas(2015,2020)")
        db_conn.close()
        return list(db_result)
    except:
        return db_error(db_conn)

def db_getUserData(username):
    '''
    Busca en la BD el usuario, contraseña y saldo a partir del username
    que nos dan en el login. Devolvemos el resultado de la query de abajo.
    '''
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()
        db_result = db_conn.execute("SELECT username, password, income FROM customers WHERE username="+"'"+str(username)+"'")
        db_conn.close()
        return list(db_result)
    except:
        return db_error(db_conn)

def db_createCustomer(username, password, email, credit, income):
    '''
    Crea una nueva fila con un nuevo usuario con los parametros.
    '''
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()
        db_conn.execute("INSERT INTO customers(email, creditcard, username, password, income) VALUES ("+
                        "'"+str(email)+"', '"+str(credit)+"', '"+str(username)+"', '"+
                        str(password)+"', "+str(income)+");")
        db_conn.close()
        return 1
    except:
        return db_error(db_conn)

def db_actualizarIncome(saldo, usuario):
    '''
    Actualiza el income del usuario con el nuevo saldo.
    '''
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()
        db_conn.execute("UPDATE customers "+
                        "SET income="+str(saldo)+
                        " WHERE username="+"'"+str(usuario)+"';"
                       )
        db_conn.close()
        return 1
    except:
        return db_error(db_conn)

def get_id_usuario(usuario):
    '''
    Actualiza el income del usuario con el nuevo saldo.
    '''
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()
        db_result = db_conn.execute("Select customerid from customers where username = '"+str(usuario)+"'")
        resultado = list(db_result)
        db_conn.close()
        return resultado[0][0]
    except:
        return db_error(db_conn)

def getHistorial(idusuario):
    '''
    Actualiza el income del usuario con el nuevo saldo.
    '''
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()
        i = 1
        historial = {"compras": []}
        db_result = db_conn.execute("Select orderid from orders where customerid = '"+str(idusuario)+"' and status is not null")
        resultado = list(db_result)


        if len(resultado) != 0:
            for o in resultado:
                prize = 0
                pedido_actual = {}
                pedido_actual['numero_pedido'] = i
                pedido_actual['orderid'] = o[0]
                db_result2= db_conn.execute("Select orderdate, status from orders where orderid = '"+str(o[0])+"'")
                resultado2 = list(db_result2)
                pedido_actual['fecha_pedido'] = resultado2[0][0]
                pedido_actual['status'] = resultado2[0][1]

                pedido_actual['peliculas'] = []
                db_result1 = db_conn.execute("Select prod_id from orderdetail where orderid = '"+str(o[0])+"'")
                resultado1 = list(db_result1)
                i = i+1
                for p in resultado1:
                    db_result3 = db_conn.execute("Select movietitle from products as p, imdb_movies as m where p.prod_id = '"+str(p[0])+"' and p.movieid = m.movieid")
                    resultado3 = list(db_result3)
                    db_result4 = db_conn.execute("Select quantity, price from orderdetail where orderid ='"+str(o[0])+"' and prod_id = '"+str(p[0])+"'")
                    resultado4 = list(db_result4)
                    prize = prize + (float(resultado4[0][1]) * float(resultado4[0][0]))
                    pedido_actual['peliculas'].append({"id": p[0], "precio": resultado4[0][1],  "titulo": resultado3[0][0], "cantidad": resultado4[0][0]})

                pedido_actual['precio_total'] = prize
                historial['compras'].append(pedido_actual)

        return historial['compras']

        db_conn.close()
        return resultado[0][0]
    except:
        return db_error(db_conn)
