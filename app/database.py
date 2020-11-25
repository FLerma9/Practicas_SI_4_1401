import os
import sys, traceback
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, text
from sqlalchemy.sql import select

# configurar el motor de sqlalchemy
db_engine = create_engine("postgresql://alumnodb:alumnodb@localhost/si1", echo=False)
db_meta = MetaData(bind=db_engine)
# cargar una tabla
db_table_orders = Table('orders', db_meta, autoload=True, autoload_with=db_engine)
db_table_orderdetail = Table('orderdetail', db_meta, autoload=True, autoload_with=db_engine)

def get_id_pedido(user):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        # Sacar el id del pedido si el usuario tiene alguno
        db_result = db_conn.execute("Select orderid from orders as o, customers as c where c.customerid = o.customerid and c.username ='"+user+"' and o.status is null")

        db_conn.close()

        return list(db_result)[0][0]
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
            db_result1 = db_conn.execute("Select movietitle, m.movieid from imdb_movies as m, products as p where p.prod_id = '" +str(o[0])+"' and p.movieid = m.movieid")
            title = list(db_result1)
            order_final.append({"id": title[0][1], "titulo": title[0][0], "precio": float(o[1]), "cantidad": int(o[2])})
        resultado = {'Peliculas': order_final}
        db_conn.close()

        return  resultado
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

        return float(list(db_result)[0][0])
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

        db_conn.execute("insert into orders (orderdate, customerid, taxnumeric, status) values(NOW(), '"+str(usuario[0][0])+"', 15, NULL)")

        db_result1 = db_conn.execute("Select orderid from orders where customerid = '" +str(usuario[0][0])+ "' and status is null")
        id_order = list(db_result1)

        if pedido:
            for p in pedido:
                db_result2 = db_conn.execute("Select prod_id from products as p where p.movieid = '" +str(p['id'])+ "'")
                prodid = list(db_result)

                db_conn.execute("insert into orderdetail (orderid, prod_id, price, quantity) values('"+str(id_order[0][0])+"', '"+str(prodid[0][0])+"', '"+str(p['precio'])+"', '"+p['cantidad']+"')")

        db_conn.close()

        return float(list(db_result)[0][0])
    except:
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return 'Something is broken'

def peli_in_order(pelicula, pedido):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        # Sacar el id del pedido si el usuario tiene alguno
        db_result = db_conn.execute("Select prod_id from orders as o, orderdetail as od where o.orderid = '" +str(pedido)+ "' and o.orderid = od.orderid")
        order = list(db_result)
        print("hey")
        for o in order:
            db_result1 = db_conn.execute("Select movietitle from imdb_movies as m, products as p where p.prod_id = '" +str(o[0])+"' and p.movieid ='" +str(pelicula)+ "'")
            if list(db_result1):
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

def create_peli(pelicula, pedido):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        # Sacar el id del pedido si el usuario tiene alguno
        db_result = db_conn.execute("Select prod_id, price, movietitle from products as p, imdb_movies as m where p.movieid = '" +str(pelicula)+ "' and m.movieid = '" +str(pelicula)+"'")
        peli = list(db_result)

        db_conn.execute("insert into orderdetail values("+str(pedido)+", "+str(peli[0][0])+", " +str(peli[0][1])+", 1)")

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

def add_peli(pelicula, pedido):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        # Sacar el id del pedido si el usuario tiene alguno
        db_result = db_conn.execute("Select prod_id from products as p where p.movieid = '" +str(pelicula)+ "'")
        prodid = list(db_result)
        db_result1 = db_conn.execute("Select quantity from orderdetail as od where od.orderid = '" +str(pedido)+ "' and od.prod_id = '" +str(prodid[0][0])+"'")
        cantidad = list(db_result1)

        cantidadfinal = cantidad[0][0] + 1
        db_conn.execute("update orderdetail set quantity = '" +str(cantidadfinal)+"' where orderid = '" +str(pedido)+ "' and prod_id = '" +str(prodid[0][0])+"'")

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

def rmv_pelicula(pelicula, pedido):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()
        print(pelicula)

        # Sacar el id del pedido si el usuario tiene alguno
        db_result = db_conn.execute("Select prod_id from products as p where p.movieid = '" +str(pelicula)+ "'")
        prodid = list(db_result)
        print("999999999999999999999999")
        print(prodid)
        print("999999999999999999999999")
        db_result1 = db_conn.execute("Select quantity from orderdetail as od where od.orderid = '" +str(pedido)+ "' and od.prod_id = '" +str(prodid[0][0])+"'")
        cantidad = list(db_result1)
        print(cantidad)

        if cantidad[0][0] > 1:
            cantidadfinal = cantidad[0][0] - 1
            db_conn.execute("update orderdetail set quantity = '" +str(cantidadfinal)+"' where orderid = '" +str(pedido)+ "' and prod_id = '" +str(prodid[0][0])+"'")
        else:
            db_conn.execute("delete from orderdetail where orderid = '" +str(pedido)+ "' and prod_id = '" +str(prodid[0][0])+"'")


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

def act_pelicula(pelicula, pedido, cantidad1):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        # Sacar el id del pedido si el usuario tiene alguno
        db_result = db_conn.execute("Select prod_id from products as p where p.movieid = '" +str(pelicula)+ "'")
        prodid = list(db_result)
        db_result1 = db_conn.execute("Select quantity from orderdetail as od where od.orderid = '" +str(pedido)+ "' and od.prod_id = '" +str(prodid[0][0])+"'")
        cantidad = list(db_result1)

        cantidadfinal = cantidad1
        db_conn.execute("update orderdetail set quantity = '" +str(cantidadfinal)+"' where orderid = '" +str(pedido)+ "' and prod_id = '" +str(prodid[0][0])+"'")

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
