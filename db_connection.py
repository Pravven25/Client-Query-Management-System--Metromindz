import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'query_db.sqlite')

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    return conn

def create_tables():
    """Create all necessary tables"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS client_queries (
                query_id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_name TEXT,
                mail_id TEXT NOT NULL,
                mobile_number TEXT NOT NULL,
                query_heading TEXT NOT NULL,
                query_description TEXT NOT NULL,
                status TEXT DEFAULT 'Open',
                priority TEXT DEFAULT 'Medium',
                query_created_time DATETIME NOT NULL,
                query_closed_time DATETIME,
                assigned_to TEXT
            )
        """)
        
        db.commit()
        cursor.close()
        db.close()
        print("✅ Tables created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("Testing database connection...")
    if create_tables():
        print("✅ Database setup complete!")
    else:
        print("❌ Database setup failed!")