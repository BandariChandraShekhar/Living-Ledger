"""Create a sample SQLite database for testing"""
import sqlite3
import random
from datetime import datetime, timedelta

def create_sample_database(db_path: str = "sample_data.db"):
    """Create a sample database with realistic data"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create customers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY,
            email TEXT NOT NULL,
            first_name TEXT,
            last_name TEXT,
            phone TEXT,
            created_at TEXT,
            status TEXT,
            total_purchases REAL
        )
    """)
    
    # Create orders table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            order_date TEXT,
            total_amount REAL,
            status TEXT,
            payment_method TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        )
    """)
    
    # Create products table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY,
            product_name TEXT NOT NULL,
            category TEXT,
            price REAL,
            stock_quantity INTEGER,
            supplier_id INTEGER,
            is_active INTEGER
        )
    """)
    
    # Insert sample customers
    statuses = ['active', 'inactive', 'pending', 'suspended']
    first_names = ['John', 'Jane', 'Bob', 'Alice', 'Charlie', 'Diana', 'Eve', 'Frank']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis']
    
    for i in range(1, 101):
        email = f"user{i}@example.com"
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        phone = f"+1-555-{random.randint(1000, 9999)}"
        created_at = (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat()
        status = random.choice(statuses)
        total_purchases = round(random.uniform(0, 10000), 2)
        
        cursor.execute("""
            INSERT INTO customers (customer_id, email, first_name, last_name, phone, created_at, status, total_purchases)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (i, email, first_name, last_name, phone, created_at, status, total_purchases))
    
    # Insert sample orders
    order_statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
    payment_methods = ['credit_card', 'debit_card', 'paypal', 'bank_transfer']
    
    for i in range(1, 251):
        customer_id = random.randint(1, 100)
        order_date = (datetime.now() - timedelta(days=random.randint(1, 180))).isoformat()
        total_amount = round(random.uniform(10, 1000), 2)
        status = random.choice(order_statuses)
        payment_method = random.choice(payment_methods)
        
        cursor.execute("""
            INSERT INTO orders (order_id, customer_id, order_date, total_amount, status, payment_method)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (i, customer_id, order_date, total_amount, status, payment_method))
    
    # Insert sample products
    categories = ['Electronics', 'Clothing', 'Books', 'Home & Garden', 'Sports', 'Toys']
    product_names = [
        'Laptop', 'Smartphone', 'Headphones', 'T-Shirt', 'Jeans', 'Novel',
        'Cookbook', 'Garden Tools', 'Basketball', 'Action Figure', 'Tablet',
        'Smartwatch', 'Sneakers', 'Backpack', 'Desk Lamp'
    ]
    
    for i in range(1, 51):
        product_name = random.choice(product_names) + f" Model {i}"
        category = random.choice(categories)
        price = round(random.uniform(5, 500), 2)
        stock_quantity = random.randint(0, 1000)
        supplier_id = random.randint(1, 10)
        is_active = random.choice([0, 1])
        
        cursor.execute("""
            INSERT INTO products (product_id, product_name, category, price, stock_quantity, supplier_id, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (i, product_name, category, price, stock_quantity, supplier_id, is_active))
    
    conn.commit()
    conn.close()
    
    print(f"Sample database created: {db_path}")
    print("Tables: customers (100 rows), orders (250 rows), products (50 rows)")

if __name__ == "__main__":
    create_sample_database()
