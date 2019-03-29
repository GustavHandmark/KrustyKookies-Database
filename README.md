# EDAF75, project report

This is the report for

 + Daniel Regefalk, `ine15dre`
 + Fredrik Olsson, `ine15fol`
 + Gustav Handmark, `jup14gha`

We solved this project on our own, except for:

 + The Peer-review meeting


## ER-design

The model is in the file [`er-model.png`](er-model.png):

<center>
    <img src="er-model.png" width="100%">
</center>

## Relations

### TODO: 

+ recipes(**recipe_name**)
+ ingredients(**ingredient_name**, unit, total_quantity, last_delivery_amount, last_delivery_date)
+ recipie_ingredients(_recipe_name_, _ingredient_name_)
+ pallets(**pallet_id**, blocked, production_date, shipping_date, delivery_date)
+ orders(**order_id**, order_created_date, order_delivery_date)
+ pallets(**customer_id**, name, address)


## Scripts to set up database

The script used to set up the database is:

 + [`server/database.sql`](server/database.sql) (defines the tables)

To create the database, we run:

```shell
sqlite3 server/krusty-db.sqlite < server/database.sql
```

Using the `/reset` endpoint populates the database.

## How to compile and run the program

Tun the program from the command line with:

```shell
python3 server/server.py
```