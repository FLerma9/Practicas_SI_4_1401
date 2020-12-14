import os
import sys, traceback
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, text
from sqlalchemy.sql import select
from sqlalchemy import func
from pymongo import MongoClient

# configurar el motor de sqlalchemy
db_engine = create_engine("postgresql://alumnodb:alumnodb@localhost/si1", echo=False)
db_meta = MetaData(bind=db_engine)

def db_error(db_conn):
    '''
    Devuelve e informa del error de sqlalchemy.
    '''
    if db_conn is not None:
        db_conn.close()
    print("Exception in DB access:")
    print("-"*60)
    traceback.print_exc(file=sys.stderr)
    print("-"*60)
    return 'Something is broken'

def createMongoDatabase():
    '''
    Crea la BD en MongoDB llamada si1, si ya existia la borra y la vuelve a crear.
    '''
    myclient = MongoClient("mongodb://localhost:27017/")
    dblist = myclient.list_database_names()
    mydb = myclient["si1"]
    if "si1" in dblist:
      print("Ya existe la BD llamada si1 en MongoDB.\n")
      myclient.drop_database("si1")
      mydb = myclient["si1"]
    return mydb

def createCollection(mydb):
    '''
    Crea la coleccion topUSA en la BD de MongoDB llamada si1.
    '''
    collist = mydb.list_collection_names()
    mycol = mydb["topUSA"]
    if "topUSA" in collist:
        print("Ya existe la coleccion topUSA.\n")
        mycol.drop()
        mycol = mydb["topUSA"]
    return mycol

def db_getTopUsa():
    '''
    Realiza una query PostgreSQL que recibe el id, el titulo y el año
    de las peliculas cuyo pais es USA (las 800 más recientes, por eso
    ponemos de limite 800 y ordenamos por anio descendentemente.)
    '''
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()
        db_result = db_conn.execute("SELECT DISTINCT m.movieid, movietitle, year " +
                                    "FROM imdb_movies AS m " +
                                    "INNER JOIN imdb_moviecountries AS c " +
                                    "ON m.movieid=c.movieid " +
                                    "WHERE country='USA' " +
                                    "ORDER BY year DESC, movietitle " +
                                    "LIMIT 800;")
        db_conn.close()
        return list(db_result)
    except:
        return db_error(db_conn)

def db_getGenres(id):
    '''
    Realiza una query PostgreSQL que recibe todos los generos de una pelicula
    cuyo id pasamos como argumento. Devuelve la lista con los generos.
    '''
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()
        db_result = db_conn.execute("SELECT genre FROM imdb_moviegenres " +
                                    "WHERE movieid=" + str(id) +
                                    " GROUP BY genre;")
        db_conn.close()
        genres = []
        for genre in list(db_result):
            genres.append(genre.genre)
        return genres
    except:
        return db_error(db_conn)

def insertGenresMongo(mycol):
    '''
    Por cada pelicula de las 800 que hay en la coleccion, buscamos en la BD
    de postgresql los generos que tiene, y actualizamos la base de datos
    de mongo con la nueva informacion
    '''
    for peli in mycol.find():
        genres = db_getGenres(peli["_id"])
        mycol.update_one({ "title": peli["title"] }, { "$set": { "genres": genres } })

def db_getActors(id):
    '''
    Realiza una query PostgreSQL que recibe todos los actores de una pelicula
    cuyo id pasamos como argumento. Devuelve la lista con los actores.
    '''
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()
        db_result = db_conn.execute("SELECT actorname FROM imdb_actors AS a " +
                                    "INNER JOIN public.imdb_actormovies as m " +
                                    "ON a.actorid = m.actorid " +
                                    "WHERE m.movieid=" + str(id) + ";")
        db_conn.close()
        actors = []
        for actor in list(db_result):
            actors.append(actor.actorname)
        return actors
    except:
        return db_error(db_conn)

def insertActorsMongo(mycol):
    '''
    Por cada pelicula de las 800 que hay en la coleccion, buscamos en la BD
    de postgresql los actores que tiene, y actualizamos la base de datos
    de mongo con la nueva informacion
    '''
    for peli in mycol.find():
        actors = db_getActors(peli["_id"])
        mycol.update_one({ "title": peli["title"] }, { "$set": { "actors": actors } })

def db_getDirectors(id):
    '''
    Realiza una query PostgreSQL que recibe todos los directores de una pelicula
    cuyo id pasamos como argumento. Devuelve la lista con los directores.
    '''
    try:
        # conexion a la base de datos
        db_conn = None
        db_conn = db_engine.connect()
        db_result = db_conn.execute("SELECT directorname FROM imdb_directors AS d " +
                                    "INNER JOIN public.imdb_directormovies as m " +
                                    "ON d.directorid = m.directorid " +
                                    "WHERE m.movieid=" + str(id) + ";")
        db_conn.close()
        directors = []
        for director in list(db_result):
            directors.append(director.directorname)
        return directors
    except:
        return db_error(db_conn)

def insertDirectorsMongo(mycol):
    '''
    Por cada pelicula de las 800 que hay en la coleccion, buscamos en la BD
    de postgresql los directores que tiene, y actualizamos la base de datos
    de mongo con la nueva informacion
    '''
    for peli in mycol.find():
        directors = db_getDirectors(peli["_id"])
        mycol.update_one({ "title": peli["title"] }, { "$set": { "directors": directors } })

def insertMostRelated(mycol):
    '''
    Por cada pelicula en la coleccion hace una query en MongoDB que se encarga de buscar
    que otras peliculas tienen exactamente la misma lista de géneros, y coinciden al
    100% (seleccionamos las 10 mas recientes), y actualizamos la lista de most
    related con la nueva. En la query se excluye a la propia pelicula, tal y como
    se pide.
    '''
    for peli in mycol.find():
        list = []
        for x in mycol.find({"$and":[{"_id": { "$ne": peli["_id"]} }, {"genres": peli["genres"] }]}, { "_id": 0, "title": 1, "year": 1}).sort("title").sort("Year").limit(10):
            list.append(x)
        mycol.update_one({ "title": peli["title"] }, { "$set": { "most_related_movies": list } })

def insertRelated(mycol):
    '''
    Por cada pelicula en la coleccion hace una query en MongoDB que devuelve todas las pelis
    (primero las mas recientes).
    Por cada peli devuelta, miramos sus géneros y si la mitad de sus géneros coincide
    con los géneros de la primera pelicula, entonces aniadimos esta pelicula a la lista
    de related. Cuando llegamos a 10 pasamos a la siguiente pelicula. Si la pelicula
    solo tiene un género se queda la lista vacía.
    '''
    for peli in mycol.find():
        # Si solo tiene un genero no hacemos nada
        if len(peli["genres"]) == 1:
            continue
        list = []
        # Calculamos la mitad de los géneros para mirar coincidencias.
        # Si es impar redondeamos por arriba.
        media = (len(peli["genres"])//2)+1
        for x in mycol.find({}, {"_id": 0, "title": 1, "year": 1, "genres":1}).sort("title").sort("Year"):
            count = 0
            # Calculamos cuantos generos coinciden
            for genre in x["genres"]:
                if genre in peli["genres"]:
                    count += 1
            # Si coinciden la mitad la aniadimos
            if count == media:
                list.append({"title": x["title"], "year": x["year"]})
            # Si la longitud es 10 paramos
            if len(list) == 10:
                break
        mycol.update_one({ "title": peli["title"] }, { "$set": { "related_movies": list } })

def insertTitleYearMongo(mycol, data):
    '''
    Inserta en la colección los documentos, pero solo inicializa con los valores finales
    el titulo y el año de las peliculas.
    '''
    mylist = []
    i = 0
    for peli in data:
        aux_title = peli.movietitle
        aux_year = peli.year
        aux_id = peli.movieid
        mylist.append({"_id": aux_id, "title": aux_title, "genres": [], "year": aux_year, "directors": [], "actors": [],
                       "most_related_movies": [], "related_movies": []})
    mycol.insert_many(mylist)
    return mylist

if __name__ == "__main__":
    data = db_getTopUsa()
    print("Creando la base de datos si1 en MongoDB...")
    mydb = createMongoDatabase()
    print("Creando la coleccion topUSA...")
    mycol = createCollection(mydb)
    print("Introduciendo titulo y anio de las pelis...")
    mylist = insertTitleYearMongo(mycol, data)
    print("Introduciendo  géneros de las pelis...")
    insertGenresMongo(mycol)
    print("Introduciendo actores de las pelis...")
    insertActorsMongo(mycol)
    print("Introduciendo directores de las pelis...")
    insertDirectorsMongo(mycol)
    print("Introduciendo most related...")
    insertMostRelated(mycol)
    print("Introduciendo related...")
    insertRelated(mycol)
