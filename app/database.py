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
        db_result = db_conn.execute("Select orderid from orders as o, customers as c where c.customerid = o.customerid and c.username ='"+user+"'")

        db_conn.close()

        return  db_result
    except:
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return 'Something is broken'

def get_carrito(user):
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()

        # Sacar las peliculas del pedido del usuario
        db_result = db_conn.execute("Select * from orders as o, orderdetail as od where o.orderid = '" +pedido+ "' and o.orderid = od.orderid")
        order = list(db_result)
        print(order)
        db_conn.close()

        return  db_result
    except:
        if db_conn is not None:
            db_conn.close()
        print("Exception in DB access:")
        print("-"*60)
        traceback.print_exc(file=sys.stderr)
        print("-"*60)

        return 'Something is broken'
