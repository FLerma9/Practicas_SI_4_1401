# -*- coding: utf-8 -*-

import os
import sys, traceback, time

from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, text
# configurar el motor de sqlalchemy
db_engine = create_engine("postgresql://alumnodb:alumnodb@localhost/si1", echo=False, execution_options={"autocommit":False})


def dbConnect():
    return db_engine.connect()


def dbCloseConnect(db_conn):
    db_conn.close()


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
    'Something is broken'


def delCustomer(customerid, bFallo, bSQL, duerme, bCommit):
    '''
    Realiza la transaccion de borrados del customer cuyo id recibe como
    argumento.
    args:
    -customerid : id fdel customer a borrar
    -bFallo: contiene si queremos una transaccion erronea o no
    -bSQL: contiene si queremos SQL o sqlalchemy
    -duerme: segundos a dormir por el sleep
    -bCommit: contiene si accemos un commit intermedio en la transaccion erronea
    '''
    # Array de trazas a mostrar en la página
    dbr=[]
    begin = "Hacemos begin de la transaccion."
    commit = "Hacemos commit de la transaccion"
    roll = "Hacemos rollback de la transaccion"
    od = "Borrando columnas de orderdetail cuyos pedidos son del customerid=" + str(customerid)
    o = "Borrando orders del cliente con customerid=" + str(customerid)
    c = "Borrando el customer con customerid=" + str(customerid)

    try:
        db_conn = db_engine.connect()
        # Empezamos la transaccion
        db_conn.execute("BEGIN;")
        dbr.append(begin)
        # Borramos los orderdetail
        try:
            db_conn.execute("DELETE FROM orderdetail WHERE orderid" +
                            " IN (SELECT orderid FROM orders" +
                            " WHERE customerid =" + str(customerid) + " );")
            dbr.append(od)
        except:
            dbr.append("Error borrando orderdetail.")
            db_conn.execute("ROLLBACK;")
            dbr.append(roll)
            return dbr
        # Inicio transaccion erronea
        if bFallo:
            # Si hay commit intermedio lo hacemos
            if bCommit:
                db_conn.execute("COMMIT;")
                dbr.append(commit)
                db_conn.execute("BEGIN;")
                dbr.append(begin)
            # Intentamos una query erronea
            try:
                dbr.append(c)
                db_conn.execute("DELETE FROM customers WHERE customerid="+ str(customerid) + ";")
            # Si es erronea
            except:
                # Hacemos rollback y terminamos
                dbr.append("Error con la clave foránea, retornamos.")
                db_conn.execute("ROLLBACK;")
                dbr.append(roll)
                return dbr
        # Transaccion correcta
        else:
            # Borramos orders
            db_conn.execute("DELETE FROM orders WHERE customerid =" + str(customerid) + ";")
            dbr.append(o)
            #sleep
            time.sleep(6)
            # Borramos customer
            db_conn.execute("DELETE FROM customers WHERE customerid="+ str(customerid) + ";")
            dbr.append(c)
            # Hacemos commit
            db_conn.execute("COMMIT;")
            dbr.append(commit)
            db_conn.close()
            return dbr
    except:
        db_error(db_conn)
        dbr.append("Error borrando orderdetail.")
        return dbr
