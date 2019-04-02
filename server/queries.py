#clear; sqlite3 db/krusty.db < server/database.sql; python3 server/server.py;
#clear; python3 check-krusty.py;

from bottle import request, response
from bottle import route
from bottle import post, get, put, delete
import datetime
import json
import datetime
import os

import sqlite3
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__),'..','db','krusty.db')) # Should work on every OS
conn = sqlite3.connect(db_path)

def format_response(d):
    return json.dumps(d, indent=4)

@get('/ping')
def get_ping():
    response.content_type = 'application/json'
    response.status = 200
    return format_response({'data': 'pong'})

#@post('/reset')
@route('/reset', method=['GET', 'POST'])
def reset():
    c = conn.cursor()
    c.execute("DELETE FROM customers")
    c.execute("DELETE FROM cookies")
    c.execute("DELETE FROM ingredients")
    c.execute("DELETE FROM recipes")

    c.execute("""
    INSERT 
    INTO customers(name,address)
    VALUES  ('Finkakor AB','Helsingborg'),
            ('Småbröd AB', 'Malmö'),
            ('Kaffebröd AB', 'Landskrona'),
            ('Bjudkakor AB', 'Ystad'),
            ('Kalaskakor AB', 'Trelleborg'),
            ('Partykakor AB', 'Kristianstad'),
            ('Gästkakor AB', 'Hässleholm'),
            ('Skånekakor AB', 'Perstorp')
    """)
    conn.commit()
    c.execute("""
    INSERT
    INTO cookies(name)
    VALUES  ('Nut ring'),
            ('Nut cookie'),
            ('Amneris'),
            ('Tango'),
            ('Almond delight'),
            ('Berliner')
    """)
    conn.commit()
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    dates = []
    for x in range(19):
        dates.append(now)

    c.execute("""
    INSERT INTO ingredients(name,quantity,unit,last_delivery_quantity,last_delivery_date)
    VALUES  ('Flour',100000,'g',100000,?),
            ('Butter',100000,'g',100000,?),
            ('Icing sugar',100000,'g',100000,?),
            ('Roasted, chopped nuts',100000,'g',100000,?),
            ('Fine-ground nuts',100000,'g',100000,?),
            ('Ground, roasted nuts',100000,'g',100000,?),
            ('Bread crumbs',100000,'g',100000,?),
            ('Sugar',100000,'g',100000,?),
            ('Egg whites',100000,'ml',100000,?),
            ('Chocolate',100000,'g',100000,?),
            ('Marzipan',100000,'g',100000,?),
            ('Eggs',100000,'g',100000,?),
            ('Potato starch',100000,'g',100000,?),
            ('Wheat flour',100000,'g',100000,?),
            ('Sodium bicarbonate',100000,'g',100000,?),
            ('Vanilla',100000,'g',100000,?),
            ('Chopped almonds',100000,'g',100000,?),
            ('Cinnamon',100000,'g',100000,?),
            ('Vanilla sugar',100000,'g',100000,?)
    """, dates)
    conn.commit()

    c.execute("""
        INSERT INTO recipes(quantity, cookie_name, ingredient_name)
        VALUES  (450,'Nut ring','Flour'),
                (450,'Nut ring','Butter'),
                (190,'Nut ring','Icing sugar'),
                (225,'Nut ring','Roasted, chopped nuts'),
                (750,'Nut cookie','Fine-ground nuts'),
                (625,'Nut cookie','Ground, roasted nuts'),
                (125,'Nut cookie','Bread crumbs'),
                (375,'Nut cookie','Sugar'),
                (350,'Nut cookie','Egg whites'),
                (50,'Nut cookie','Chocolate'),
                (750,'Amneris','Marzipan'),
                (250,'Amneris','Butter'),
                (250,'Amneris','Eggs'),
                (25,'Amneris','Potato starch'),
                (25,'Amneris','Wheat flour'),
                (200,'Tango','Butter'),
                (250,'Tango','Sugar'),
                (300,'Tango','Flour'),
                (4,'Tango','Sodium bicarbonate'),
                (2,'Tango','Vanilla'),
                (400,'Almond delight','Butter'),
                (270,'Almond delight','Sugar'),
                (279,'Almond delight','Chopped almonds'),
                (400,'Almond delight','Flour'),
                (10,'Almond delight','Cinnamon'),
                (350,'Berliner','Flour'),
                (250,'Berliner','Butter'),
                (100,'Berliner','Icing sugar'),
                (50,'Berliner','Eggs'),
                (5,'Berliner','Vanilla sugar'),
                (50,'Berliner','Chocolate')
    """
    )
    conn.commit()

    response.content_type = 'application/json'
    response.status = 200
    return format_response({"status": 'ok'})

@get('/customers')
def get_customers():
    c = conn.cursor()
    c.execute("""
        SELECT name, address
        FROM customers
    """)
    s = {"customers": [{"name": name, "address": address} for (name, address) in c]}

    response.content_type = 'application/json'
    response.status = 200
    return format_response(s)


@get('/ingredients')
def get_ingredients():
    c = conn.cursor()
    c.execute("""
        SELECT name, quantity, unit
        FROM ingredients
    """)
    s = {"ingredients": [{"name": name, "quantity": quantity, "unit": unit} for (name, quantity, unit) in c]}
    
    response.content_type = 'application/json'
    response.status = 200
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
    s = {"cookies": [{"name": name[0]} for (name) in c]} #Query will always return a tuple.
    
    response.content_type = 'application/json'
    response.status = 200
    return format_response(s)


@get('/recipes')
def get_recipes():
    c = conn.cursor()
    c.execute("""
        SELECT cookie_name,ingredient_name,recipes.quantity,unit
        FROM recipes
        JOIN ingredients ON ingredient_name == name
        ORDER BY cookie_name, ingredient_name
    """)
    s = {"recipes": [{"cookie": cookie, "ingredient": ingredient, "quantity": quantity, "unit": unit} for (cookie, ingredient, quantity, unit) in c]}
    
    response.content_type = 'application/json'
    response.status = 200
    return format_response(s)


#curl -X POST http://localhost:8888/pallets -d "cookie=Tango"
@post('/pallets')
def create_pallet():
    cookie_name = request.query.cookie
    c = conn.cursor()

    try:
        c.execute(
        """
            INSERT
            INTO    pallets(production_date, cookie_name)
            VALUES  (?, ?)
        """, [datetime.datetime.now().strftime("%Y-%m-%d"), cookie_name]
        )
        conn.commit()
    except Exception as e:
        if str(e) == "Insufficient ingredients!":
            response.content_type = 'application/json'
            response.status = 200
            return format_response({'status': 'not enough ingredients'})

    response.content_type = 'application/json'
    response.status = 200
    return format_response({'status': 'ok'})


@get('/pallets')
def get_pallets():
    after = request.query.after
    before = request.query.before
    cookie_name = request.query.cookie
    blocked = request.query.blocked


    c = conn.cursor()
    c.execute("""
        SELECT  id, cookie_name, production_date, order_id, blocked
        FROM    pallets
        WHERE   (production_date > ? OR ? = "") AND
                (production_date < ? OR ? = "") AND
                (cookie_name = ? OR ? = "") AND
                (blocked = ? OR ? = "")
    """,
        [after, after, before, before, cookie_name, cookie_name, blocked, blocked]
    )

    s = [{
        "id": id,
        "cookie": cookie,
        "productionDate": production_date,
        "customer": customer,
        "blocked": True if blocked == 1 else False
    } for (id, cookie, production_date, customer, blocked) in c]


    response.content_type = 'application/json'
    response.status = 200
    return format_response({'pallets': s})


@route('/block/<cookie_name>/<from_date>/<to_date>', method=['GET', 'POST'])
def block(cookie_name, from_date, to_date):
    setBlocked(1, cookie_name, from_date, to_date)

    response.content_type = 'application/json'
    response.status = 200
    return format_response({"status": 'ok'})


@route('/unblock/<cookie_name>/<from_date>/<to_date>', method=['GET', 'POST'])
def unblock(cookie_name, from_date, to_date):
    setBlocked(0, cookie_name, from_date, to_date)

    response.content_type = 'application/json'
    response.status = 200
    return format_response({"status": 'ok'})


def setBlocked(blocked, cookie_name, from_date, to_date):
    c = conn.cursor()
    c.execute("""
        UPDATE pallets
        SET blocked = ?
        WHERE cookie_name = ? AND production_date >= ? AND production_date <= ?
    """, [blocked, cookie_name, from_date, to_date])
    conn.commit()