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

def createMongoDatabase():
    myclient = MongoClient("mongodb://localhost:27017/")
    dblist = myclient.list_database_names()
    mydb = myclient["si1"]
    if "si1" in dblist:
      print("Ya existe la BD llamada si1 en MongoDB.\n")
      myclient.drop_database("si1")
      mydb = myclient["si1"]
    return mydb

def createCollection(mydb):
    collist = mydb.list_collection_names()
    mycol = mydb["topUSA"]
    if "topUSA" in collist:
        print("Ya existe la coleccion topUSA.\n")
        mycol.drop()
        mycol = mydb["topUSA"]
    return mycol

def db_getTopUsa():
    '''
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
    for peli in mycol.find():
        genres = db_getGenres(peli["_id"])
        mycol.update_one({ "title": peli["title"] }, { "$set": { "genres": genres } })

def db_getActors(id):
    '''
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
    for peli in mycol.find():
        actors = db_getActors(peli["_id"])
        mycol.update_one({ "title": peli["title"] }, { "$set": { "actors": actors } })

def db_getDirectors(id):
    '''
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
    for peli in mycol.find():
        directors = db_getDirectors(peli["_id"])
        mycol.update_one({ "title": peli["title"] }, { "$set": { "directors": directors } })

def insertMostRelated(mycol):
    for peli in mycol.find():
        list = []
        for x in mycol.find({"$and":[{"_id": { "$ne": peli["_id"]} }, {"genres": peli["genres"] }]}, { "_id": 0, "title": 1, "year": 1}).sort("title").sort("Year").limit(10):
            list.append(x)
        mycol.update_one({ "title": peli["title"] }, { "$set": { "most_related_movies": list } })

def insertRelated(mycol):
    for peli in mycol.find():
        if len(peli["genres"]) == 1:
            continue
        list = []
        media = (len(peli["genres"])//2)+1
        for x in mycol.find({}, {"_id": 0, "title": 1, "year": 1, "genres":1}).sort("title").sort("Year"):
            count = 0
            for genre in x["genres"]:
                if genre in peli["genres"]:
                    count += 1
            if count == media:
                list.append({"title": x["title"], "year": x["year"]})
            if len(list) == 10:
                break
        mycol.update_one({ "title": peli["title"] }, { "$set": { "related_movies": list } })

def insertTitleYearMongo(mycol, data):
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
    #for peli in data:
    #    print(peli.movietitle, peli.year)
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
    #for x in mycol.find({"$and":[{"title" : {"$regex" : ".*Life.*"}}, { "genres": { "$in": ["Comedy"] } }, {"year" : {"$regex" : ".*1997.*"}}]}).sort("title").sort("Year"):
    #    print(x)
    #for x in mycol.find({"$and":[{ "directors": { "$in": ['Allen, Woody'] } }, {"year" : {"$regex" : ".*199[0-9].*"}}]}).sort("title").sort("Year"):
    #    print(x)
    #for x in mycol.find({ "actors": { "$all": [ "Galecki, Johnny", "Parsons, Jim (II)"] } }).sort("title").sort("Year"):
    #    print(x)
