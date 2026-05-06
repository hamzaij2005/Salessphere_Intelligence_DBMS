import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# ── CONFIG ── change these if needed ──────────────────────────
HOST     = "localhost"
PORT     = 5432
DB_NAME  = "Hamza"
USER     = "postgres"
PASSWORD = "Rizwana2020"
# ──────────────────────────────────────────────────────────────

def get_conn(dbname=DB_NAME):
    conn = psycopg2.connect(host=HOST, port=PORT, dbname=dbname,
                            user=USER, password=PASSWORD)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    return conn

def ensure_database():
    """Create the database if it doesn't exist yet."""
    try:
        conn = get_conn(dbname="postgres")
        cur  = conn.cursor()
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
        if not cur.fetchone():
            cur.execute(f'CREATE DATABASE "{DB_NAME}"')
            print(f'✔  Database "{DB_NAME}" created.')
        else:
            print(f'✔  Database "{DB_NAME}" already exists.')
        cur.close()
        conn.close()
    except Exception as e:
        print(f"✘  Could not connect to postgres: {e}")
        raise

DDL = """
-- ── DROP ─────────────────────────────────────────────────────
DROP TABLE IF EXISTS stock_orders  CASCADE;
DROP TABLE IF EXISTS reviews       CASCADE;
DROP TABLE IF EXISTS payments      CASCADE;
DROP TABLE IF EXISTS order_items   CASCADE;
DROP TABLE IF EXISTS orders        CASCADE;
DROP TABLE IF EXISTS products      CASCADE;
DROP TABLE IF EXISTS categories    CASCADE;
DROP TABLE IF EXISTS sellers       CASCADE;
DROP TABLE IF EXISTS customers     CASCADE;
DROP TABLE IF EXISTS help          CASCADE;

-- ── TABLES ───────────────────────────────────────────────────
CREATE TABLE help (
    help_id     SERIAL PRIMARY KEY,
    description TEXT NOT NULL
);

CREATE TABLE categories (
    category_id  SERIAL PRIMARY KEY,
    name         VARCHAR(100) NOT NULL UNIQUE,
    description  TEXT
);

CREATE TABLE sellers (
    seller_id SERIAL PRIMARY KEY,
    name      VARCHAR(150) NOT NULL,
    email     VARCHAR(120) UNIQUE NOT NULL,
    phone     VARCHAR(20),
    address   TEXT
);

CREATE TABLE customers (
    customer_id   SERIAL PRIMARY KEY,
    name          VARCHAR(150) NOT NULL,
    email         VARCHAR(120) UNIQUE NOT NULL,
    address       TEXT,
    registered_on DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE TABLE products (
    product_id  SERIAL PRIMARY KEY,
    name        VARCHAR(200) NOT NULL,
    category_id INT NOT NULL REFERENCES categories(category_id),
    price       NUMERIC(10,2) NOT NULL CHECK (price > 0),
    stock       INT NOT NULL DEFAULT 0 CHECK (stock >= 0)
);

CREATE TABLE orders (
    order_id     SERIAL PRIMARY KEY,
    customer_id  INT NOT NULL REFERENCES customers(customer_id),
    order_date   TIMESTAMP NOT NULL,
    order_status VARCHAR(30) NOT NULL
        CHECK (order_status IN ('pending','processing','delivered','cancelled')),
    order_bill   NUMERIC(12,2) NOT NULL CHECK (order_bill >= 0)
);

CREATE TABLE order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id      INT NOT NULL REFERENCES orders(order_id),
    product_id    INT NOT NULL REFERENCES products(product_id),
    quantity      INT NOT NULL CHECK (quantity > 0),
    unit_price    NUMERIC(10,2) NOT NULL CHECK (unit_price > 0)
);

CREATE TABLE payments (
    payment_id SERIAL PRIMARY KEY,
    order_id   INT NOT NULL REFERENCES orders(order_id),
    amount     NUMERIC(12,2) NOT NULL CHECK (amount > 0),
    method     VARCHAR(50) NOT NULL
        CHECK (method IN ('credit_card','debit_card','bank_transfer',
                          'cash_on_delivery','digital_wallet')),
    paid_on    DATE NOT NULL
);

CREATE TABLE reviews (
    review_id   SERIAL PRIMARY KEY,
    order_id    INT NOT NULL REFERENCES orders(order_id),
    customer_id INT NOT NULL REFERENCES customers(customer_id),
    product_id  INT NOT NULL REFERENCES products(product_id),
    rating      INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment     TEXT,
    review_date DATE NOT NULL
);

CREATE TABLE stock_orders (
    lot_order_id     SERIAL PRIMARY KEY,
    seller_id        INT NOT NULL REFERENCES sellers(seller_id),
    product_id       INT NOT NULL REFERENCES products(product_id),
    lot_order_amount INT NOT NULL CHECK (lot_order_amount > 0),
    lot_order_date   DATE NOT NULL,
    lot_order_status VARCHAR(30) NOT NULL
        CHECK (lot_order_status IN ('pending','shipped','delivered','cancelled'))
);
"""

DATA = """
INSERT INTO categories (name, description) VALUES
('Electronics', 'Gadgets, phones, laptops and more'),
('Home Appliances', 'Kitchen and living room electronics'),
('Fashion', 'Clothing, shoes and accessories'),
('Books', 'Educational and fiction books'),
('Fitness', 'Gym equipment and health products');

INSERT INTO sellers (name, email, phone, address) VALUES
('Tech Hub', 'contact@techhub.com', '0300-1112223', 'Hafeez Center, Lahore'),
('Home Style', 'info@homestyle.pk', '0321-4445556', 'Gulberg, Lahore'),
('Fashion Pro', 'sales@fashionpro.com', '0333-7778889', 'Z-Block, DHA, Lahore');

INSERT INTO customers (name, email, address, registered_on) VALUES
('Ali Khan', 'ali.khan@email.com', 'Model Town, Lahore', '2022-01-10'),
('Sara Ahmed', 'sara.a@email.com', 'F-7, Islamabad', '2022-03-15'),
('Usman Sheikh', 'usman.s@email.com', 'Gulshan, Karachi', '2022-06-20'),
('Zainab Bibi', 'zainab.b@email.com', 'Peshawar Cantt', '2023-01-05'),
('Hamza Rizwan', 'hamza.r@email.com', 'Johar Town, Lahore', '2023-04-12');

INSERT INTO products (name, category_id, price, stock) VALUES
('Samsung Galaxy S23', 1, 185000.00, 45),
('iPhone 15 Pro', 1, 450000.00, 12),
('Dell XPS 15', 1, 320000.00, 8),
('JBL Flip 6', 1, 25000.00, 120),
('Sony WH-1000XM5', 1, 85000.00, 30),
('Philips Air Fryer', 2, 35000.00, 65),
('Kenwood Microwave', 2, 28000.00, 40),
('Nike Air Max', 3, 45000.00, 25),
('Adidas Ultraboost', 3, 38000.00, 50),
('Levis 501 Jeans', 3, 12000.00, 100),
('Python Crash Course', 4, 4500.00, 200),
('Atomic Habits', 4, 3200.00, 150),
('Yoga Mat', 5, 2500.00, 300),
('Adjustable Dumbbells', 5, 15000.00, 20);

INSERT INTO orders (customer_id, order_date, order_status, order_bill) VALUES
(1, '2023-10-15 10:30:00', 'delivered', 185000.00),
(2, '2023-11-02 14:45:00', 'delivered', 35000.00),
(3, '2023-12-20 09:15:00', 'delivered', 12000.00),
(4, '2024-01-10 16:20:00', 'delivered', 3200.00),
(5, '2024-02-14 11:00:00', 'processing', 45000.00);

INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
(1, 1, 1, 185000.00),
(2, 6, 1, 35000.00),
(3, 10, 1, 12000.00),
(4, 12, 1, 3200.00),
(5, 8, 1, 45000.00);

INSERT INTO payments (order_id, amount, method, paid_on) VALUES
(1, 185000.00, 'bank_transfer', '2023-10-15'),
(2, 35000.00, 'credit_card', '2023-11-02'),
(3, 12000.00, 'cash_on_delivery', '2023-12-20'),
(4, 3200.00, 'digital_wallet', '2024-01-10'),
(5, 45000.00, 'debit_card', '2024-02-14');

INSERT INTO reviews (order_id, customer_id, product_id, rating, comment, review_date) VALUES
(1, 1, 1, 5, 'Excellent phone, high quality camera.', '2023-10-20'),
(2, 2, 6, 4, 'Very useful for healthy cooking.', '2023-11-10'),
(3, 3, 10, 5, 'Perfect fit and original product.', '2023-12-25');

INSERT INTO stock_orders (seller_id, product_id, lot_order_amount, lot_order_date, lot_order_status) VALUES
(1, 1, 50, '2023-09-01', 'delivered'),
(2, 6, 30, '2023-10-15', 'delivered'),
(3, 8, 20, '2023-11-20', 'delivered');
"""

def setup():
    ensure_database()
    conn = get_conn()
    cur  = conn.cursor()
    try:
        print("Creating tables...")
        cur.execute(DDL)
        print("Inserting sample data...")
        cur.execute(DATA)
        conn.commit()
        print("✔  Database setup complete.")
    except Exception as e:
        conn.rollback()
        print(f"✘  Setup failed: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    setup()
