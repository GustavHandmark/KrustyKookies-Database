from bottle import request, response
from bottle import route
from bottle import post, get, put, delete
import json
import datetime

import sqlite3
conn = sqlite3.connect("krusty-db.sqlite")


def format_response(d):
    return json.dumps(d,indent = 4) + '\n'

@get('/ping')
def get_ping():
    response.content_type = 'application/json'
    response.status = 200
    return format_response({'data':'pong'})

@post('/reset')
def reset():

    return

@get('/customers')
def get_customers():
    c = conn.cursor()
    c.execute("""
        SELECT *
        FROM customers
    """)
    s = {"customers":[{"name":name,"address":address} for (name, address) in c]}
    return format_response(s)

@get('/ingredients')
def get_ingredients():
    c = conn.cursor()
    c.execute("""
        SELECT *
        FROM ingredients
    """)
    s = {"ingredients":[{"name":name,"quantity":quantity,"unit":unit} for (name, unit, quantity) in c]}
    return format_response(s)

@get('/cookies')
def get_cookies():
    c = conn.cursor()
    c.execute(
        """
        SELECT *
        FROM cookies
        ORDER BY name
        """
    )
    s = {"cookies":[{"name":name} for name in c]}
    return format_response(s)

@get('/recipes')
def get_recipes():
    c = conn.cursor()
    c.execute("""
        SELECT cookie_name,ingredient_name,quantity,unit
        FROM recipes
        JOIN ingredients
        USING (ingredient_name)
        ORDER BY name, ingredient
    """)
    ##Definately not gonna work, will wait until we have the db.
    s = {"recipes":[{"cookie":cookie,"ingredient":ingredient,"quantity":quantity,"unit":unit} for (cookie,ingredient, quantity, unit) in c]}
    return format_response(s)

@post('/pallets')
def create_pallet():
    data = request.json
    cookie_name = data['cookie']

    """
    {
        "status": "no such cookie"
    }

    {
        "status": "not enough ingredients"
    }

    {
        "status": "ok",
        "id": "9ff0571af3ea2b12065946f57ddd4527"
    }
    """


    c.execute(
        """
        INSERT
        INTO    pallets(production_date, cookie_name)
        VALUES  (?, ?)
        """, [datetime.datetime.now().strftime("%Y-%m-%d"), cookie_name]
    )
    conn.commit()

    return

@get('/pallets')
def get_pallets():
    """
    Parameters:

    after: restricts the search so we only get pallets produced after (not including) the given date

    before: restricts the search so we only get pallets produced before (not including) the given date

    cookie: restricts the search so we only get pallets with the given cookie

    blocked: restricts the search so we only get pallets which are blocked or non-blocked -- 0 means non-blocked, 1 means blocked
    """

    data = request.json
    after = data['after']
    before = data['before']
    cookie_name = data['cookie']
    blocked = data['blocked']

    c = conn.cursor()
    c.execute("""
        SELECT  *
        FROM    pallets
        WHERE   (production_date > ? OR ? IS NULL) AND
                (production_date < ? OR ? IS NULL) AND
                (receipe_name = ? OR ? IS NULL) AND
                (blocked = ? OR ? IS NULL)
    """, [after, after, before, before, cookie_name, cookie_name, blocked, blocked])

    s = [{
        "id": id,
        "cookie": cookie,
        "productionDate": production_date,
        "customer": customer,
        "blocked": blocked
    } for (id, cookie, prouction_date, customer, blocked) in c]

    return format_response({'data': s})


@route('/block/<cookie_name>/<from_date>/<to_date>', method=['GET','POST'])
def block(cookie_name, from_date, to_date):
    setBlocked(1, cookie_name, from_date, to_date)

@route('/unblock/<cookie_name>/<from_date>/<to_date>', method=['GET','POST'])
def unblock(cookie_name, from_date, to_date):
    setBlocked(0, cookie_name, from_date, to_date)

def setBlocked(blocked, cookie_name, from_date, to_date):
    c = conn.cursor()
    c.execute("""
        UPDATE pallets
        SET blocked = ?
        WHERE recipe_name = ? AND production_date => ? AND production_date <= ?
    """, [blocked, cookie_name, from_date, to_date])
    conn.commit()

'''
Old stuff
def format_response(d):
    return json.dumps(d,indent = 4) + '\n'


@get('/movies')
def get_movies():
    response.content_type = 'application/json'
    title = request.query.title
    year = request.query.year
    if (title and year):
        c = conn.cursor()
        c.execute("""
            SELECT *
            FROM movies
            WHERE title=? AND prod_year=?
        """,[title,year])
        s = [{"imdbKey": imdb_id, "title":title,"prod_year":prod_year}
            for (title,prod_year,imdb_id) in c]
    else:
        query = """
            SELECT *
            FROM movies
            """
        c = conn.cursor()
        c.execute(query)
        s = [{"imdbKey": imdb_id, "title":title,"prod_year":prod_year}
            for (title,prod_year,imdb_id) in c]


    return format_response({'data':s})

@get('/movies/<imdb_id>')
def search_movie(imdb_id):
    response.content_type = 'application/json'
    query = """
        SELECT *
        FROM movies
        WHERE imdb_id=?
        """
    c = conn.cursor()
    c.execute(query,[imdb_id])
    s = [{"imdbKey": imdb_id, "title":title,"prod_year":prod_year}
        for (title,prod_year,imdb_id) in c]

    return format_response({'data':s})

@route('/reset',method=['GET','POST'])
def reset_database():
    c = conn.cursor()
    c.execute("DELETE FROM users")
    c.execute("DELETE FROM movies")
    c.execute("DELETE FROM performances")
    c.execute("DELETE FROM tickets")
    c.execute("DELETE FROM theaters")

    c.execute("""
    INSERT 
    INTO users(username,u_name,password)
    VALUES  ('alice','Alice','dobido'),
            ('bob','Bob','whasinaname')
    """)
    conn.commit()
    c.execute("""
    INSERT INTO movies(title,prod_year,imdb_id)
    VALUES  ('The Shape of Water', 2017, 'tt5580390'),
            ('Moonlight', 2016, 'tt4975722'),
            ('Spotlight', 2015, 'tt1895587'),
            ('Birdman', 2014, 'tt2562232')
    """)
    conn.commit()
    c.execute("""
    INSERT INTO theaters(t_name,capacity)
    VALUES  ('Kino', 10),
            ('Södran', 16),
            ('Skandia', 100)
    """)
    conn.commit()
    response.content_type = 'application/json'
    response.status = 200
    return format_response({"data":'OK'})

@route('/performances',method=['GET','POST'])
def add_performance():
    response.content_type = 'application/json'
    imdb_id = request.query.imdb
    theater = request.query.theater
    date = request.query.date
    time = request.query.time
    if (imdb_id and theater and date and time):
        c = conn.cursor()

        c.execute("SELECT imdb_id FROM movies WHERE imdb_id = ?",[imdb_id])
        movie_exist = list(c)
        c.execute("SELECT t_name FROM theaters WHERE t_name = ?",[theater])
        theater_exist = list(c)

        if(len(movie_exist) != 0 and len(theater_exist) != 0):
            query = """
                INSERT INTO performances(imdb_id,t_name,date,time)
                VALUES (?,?,?,?)
                """
            c.execute(query,[imdb_id,theater,date,time])
            conn.commit()
            p_id=c.execute("SELECT p_id FROM performances WHERE rowid = last_insert_rowid();")
            s = c.fetchone()
        else:
            s = "No such movie or theater"

    else:
        query = """
            SELECT p_id,date,time,title,prod_year,t_name,capacity-coalesce(count(id),0)
            FROM performances
            JOIN movies
            USING(imdb_id)
            JOIN theaters
            USING(t_name)
            LEFT JOIN tickets
            USING(p_id)
            """
        c = conn.cursor()
        c.execute(query)
        a = [{"performanceId":p_id,"date":date,"startTime":time,"title":title,"year":prod_year,"theater":t_id,'remainingSeats':capacity}
            for (p_id,t_id,date,time,title,prod_year,capacity) in c]
        s={'data':a}

    return format_response(s)

@route('/tickets',methods=['GET','POST'])
def add_ticket():
    response.content_type = 'application/json'
    user = request.query.user
    p_id = request.query.performance
    pwd = request.query.pwd
    if (user and p_id and pwd):
        c = conn.cursor()
        query = """
            SELECT password
            FROM users
            WHERE username = ?
        """
        c.execute(query,[user])
        database_pw = c.fetchone()

        if(pwd == database_pw[0]):
            q = """
                SELECT capacity-coalesce(count(id),0)
                FROM performances
                LEFT JOIN tickets
                USING(p_id)
            """
            r_seats = c.fetchone()
            if(r_seats == 0):
                s= 'No remaining tickets'
            else:
                cticket = """
                    INSERT
                    INTO tickets(username,p_id)
                    VALUES (?,?)
                """
                c.execute(cticket,[user,p_id])
                conn.commit()
                t_id=c.execute("SELECT id FROM tickets WHERE rowid = last_insert_rowid();")
                s= c.fetchone()


        else:
            s = f'Wrong password' #given:{pwd} found:{database_pw[0]}
            response.status = 401
    else:
        s = 'Error'
        response.status = 400
    return format_response(s)
#http://localhost:7007/performances?imdb=tt5580390&theater=Kino&date=2019-02-22&time=19:00
'''