CREATE TABLE customers (
    id    TEXT DEFAULT (lower(hex(randomblob(16)))),
    name    TEXT,
    address    TEXT,
    PRIMARY KEY(id)
);
CREATE TABLE orders (
    id    TEXT DEFAULT (lower(hex(randomblob(16)))),
    order_created_date    DATE,
    order_delivery_date    DATE,
    customer_id    TEXT,
    PRIMARY KEY(id),
    FOREIGN KEY(customer_id) REFERENCES customers(id)
);
CREATE TABLE cookies (
    name    TEXT,
    PRIMARY KEY(name)
);
CREATE TABLE ingredients (
    name    TEXT,
    quantity    TEXT,
    unit    TEXT,
    last_delivery_quantity    TEXT,
    last_delivery_date    DATE,
    PRIMARY KEY(name)
);
CREATE TABLE pallets (
    id    TEXT DEFAULT (lower(hex(randomblob(16)))),
    production_date    DATE,
    shipping_date    DATE,
    delivery_date    DATE,
    blocked    INT DEFAULT (0),
    order_id    TEXT,
    cookie_name    TEXT,
    PRIMARY KEY(id)
    FOREIGN KEY(order_id) REFERENCES orders(id)
    FOREIGN KEY(cookie_name) REFERENCES cookies(name)
);
CREATE TABLE recipes (
    quantity    INT,
    cookie_name    TEXT,
    ingredient_name    TEXT,
    PRIMARY KEY(cookie_name,ingredient_name),
    FOREIGN KEY(cookie_name) REFERENCES cookies(name),
    FOREIGN KEY(ingredient_name) REFERENCES ingredients(name)
);
CREATE TABLE order_items (
    quantity    INT,
    cookie_name    TEXT,
    order_id    TEXT,
    PRIMARY KEY(cookie_name,order_id),
    FOREIGN KEY(cookie_name) REFERENCES cookies(name),
    FOREIGN KEY(order_id) REFERENCES orders(id)
);
