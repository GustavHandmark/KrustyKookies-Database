#!/usr/bin/env python

"""This is a horrible, horrible hack, it's certainly the ugliest piece
of code I've ever written, and its only "raison d'etre" is to help you
test your servers. The program requires Python 3.6+, and reading it is
not recommended for the faint of heart.
"""


import datetime
import json
import re
import requests


HOST="localhost"
PORT=8888


def url(resource):
    return f"http://{HOST}:{PORT}{resource}"


def response_to_dict(r):
    return dict(r.json())


def label_dicts(l, label):
    """
    """
    return {d[label]: d for d in l}


def format_response(r):
    return json.dumps(r.json(), indent=4)


def abort(msg):
    print(f"Error: {msg}")
    exit(1)


def close(x, y):
    return abs(x - y)/x < 0.001


def check_reset():
    try:
        resource = url('/reset')
        print(f'Trying curl -X POST {resource}')
        r = requests.post(resource)
        # print(format_response(r))
        res = response_to_dict(r)
        if res['status'] != 'ok':
            abort(f'POST {resource} got: {res}')
    except Exception as e:
        abort(f"Error in POST /reset: {e}")


def check_cookies(expected):
    try:
        resource = url('/cookies')
        print(f'Trying curl -X GET {resource}')
        r = requests.get(resource)
        # print(format_response(r))
        found = response_to_dict(r)['cookies']
        cookies = set(d['name'] for d in found)
        if cookies != expected:
            abort(f"Expected {expected}, found {cookies}")
        else:
            print("Found all cookies")
    except Exception as e:
        abort(f"Error in GET /cookies: {e}")


def check_customers(expected):
    try:
        resource = url('/customers')
        print(f'Trying curl -X GET {resource}')
        r = requests.get(resource)
        # print(format_response(r))
        d = label_dicts(response_to_dict(r)['customers'], 'name')
        for customer, address in expected:
            if d[customer]['address'] != address:
                abort(f"GET {resource} put {customer} in {d[customer]['address']}, it should have been {address}")
    except Exception as e:
        abort(f"Error in GET /customers: {e}")
    

def check_ingredients(expected):
    try:
        resource = url('/ingredients')
        print(f'Trying curl -X GET {resource}')
        r = requests.get(resource)
        # print(format_response(r))
        d = label_dicts(response_to_dict(r)['ingredients'], 'name')
        for i, a in expected:
            print(f'Checking inventory of {i}: ', end='')
            if close(d[i]['quantity'], a):
                print('ok')
            else:
                print()
                abort(f"Ingredients: should have had {a} of {i}, found {d[i]['quantity']}")
    except Exception as e:
        abort(f"Error in GET /ingredients: {e}")


def check_pallet_creation(cookies):
    try:
        resource = url('/pallets')
        for cookie in cookies:
            full_url = f'curl -X POST {resource}\?cookie\={cookie}'
            print(full_url)
            r = requests.post(resource, params={'cookie': cookie})
            if response_to_dict(r)['status'] != 'ok':
                abort(f'Trying {full_url}')
    except Exception as e:
        abort(f"Error in POST /pallets: {e}")


def bake_until_bust():
    try:
        resource = url('/pallets')
        cookie = 'Amneris'
        full_url = f'curl -X POST {resource}\?cookie\={cookie}'
        for k in range(1, 2):
            r = requests.post(resource, params={'cookie': cookie})
            if response_to_dict(r)['status'] != 'ok':
                abort(f"Couldn't bake enough of {cookie}")
        print(f"Could bake just enough of {cookie}")
        r = requests.post(resource, params={'cookie': cookie})
        if response_to_dict(r)['status'] != 'not enough ingredients':
            abort(f"Could bake too many {cookie}")
    except Exception as e:
        abort(f"Error in POST /pallets: {e}")


def check_blocking():
    try:
        cookie = 'Tango'
        today = str(datetime.date.today())
        block = url(f'/block/{cookie}/{today}/{today}')
        _ = requests.post(block)
        r = requests.get(url('/pallets'))
        pallets = response_to_dict(r)['pallets']
        for d in pallets:
            if d['cookie'] == cookie and not d['blocked'] or d['cookie'] != cookie and d['blocked']:
                abort("Error in blocking...")
    except Exception as e:
        abort(f"Error in test of blocking: {e}")


def main():
    check_reset()
    check_cookies({'Tango',
                   'Nut ring',
                   'Nut cookie',
                   'Berliner',
                   'Amneris',
                   'Almond delight'})
    check_customers([('Bjudkakor AB', 'Ystad'),
                     ('Finkakor AB', 'Helsingborg')])
    check_ingredients([('Butter', 100_000.0),
                       ('Chocolate', 100_000.0),
                       ('Sugar', 100_000.0),
                       ('Flour', 100_000.0)])
    check_pallet_creation(['Tango', 'Amneris', 'Tango'])
    check_ingredients([('Butter', 64900.0),
                       ('Chocolate', 100_000.0),
                       ('Sugar', 73000.0),
                       ('Flour', 67600.0)])
    bake_until_bust()
    check_ingredients([("Flour", 67600.0),
                       ("Marzipan", 19000.0),
                       ("Sugar", 73000.0)])
    check_blocking()
    print("=========================")
    print("I found no obvious errors")
    print("=========================")


if __name__ == '__main__':
    main()
