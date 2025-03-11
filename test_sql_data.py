import sqlite3
import pandas as pd

# Database path
DB_PATH = "medical_supplies.db"

# Create sample database and table
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS supplies")  # Clear old data
cursor.execute("""
CREATE TABLE supplies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Product_name TEXT,
    Barcode TEXT UNIQUE,
    Expiration_Date INTEGER,
    Category TEXT,
    Quantity INTEGER,
    Threshold INTEGER DEFAULT 10)
""")

# Insert sample data (ensure six values per row)
sample_data = [
    ("Surgical Mask", "123456789", 0, "Protective Gear", 50, 10),
    ("Gloves", "987654321", 0, "Protective Gear", 30, 15),
    ("Bandages", "112233445", 0, "First Aid", 20, 5),
    ("Thermometer", "556677889", 0, "Medical Devices", 10, 3),
    ("Hand Sanitizer", "998877665", 0, "Disinfectant", 5, 2)
]

cursor.executemany(
    "INSERT INTO supplies (Product_name, Barcode, Expiration_Date, Category, Quantity, Threshold) VALUES (?, ?, ?, ?, ?, ?)",
    sample_data
)

conn.commit()

# Delete a specific item
cursor.execute("DELETE FROM supplies WHERE Barcode = '123456789'")
conn.commit()

# Update quantity of a specific item
cursor.execute("""
    UPDATE supplies
    SET Quantity = 100 
    WHERE Barcode = '987654321'
""")
conn.commit()

conn.close()

print("SQLite database with test data created successfully!")
