import subprocess
import sys
import hashlib

def install_packages():
    """Install required packages"""
    packages = ['streamlit', 'pandas', 'mysql-connector-python', 'plotly']
    
    for package in packages:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"Successfully installed {package}")
        except subprocess.CalledProcessError:
            print(f"Failed to install {package}")

def setup_database():
    """Setup database with tables and default users"""
    try:
        from db_connection import create_tables, get_db
        
        if create_tables():
            db = get_db()
            cursor = db.cursor()
            
            def hash_pw(password):
                return hashlib.sha256(password.encode()).hexdigest()
            
            default_users = [
                ("client1", "password123", "Client", "client1@example.com"),
                ("support1", "password123", "Support", "support1@example.com"),
                ("admin", "admin123", "Support", "admin@example.com")
            ]
            
            for username, password, role, email in default_users:
                try:
                    cursor.execute(
                        "INSERT INTO users (username, password, role, email) VALUES (?, ?, ?, ?)",
                        (username, hash_pw(password), role, email)
                    )
                except:
                    pass
            
            db.commit()
            cursor.close()
            db.close()
            
            print("✅ Database setup completed!")
            print("Default users created:")
            print("Client: username='client1', password='password123'")
            print("Support: username='support1', password='password123'")
            print("Admin: username='admin', password='admin123'")
        
    except Exception as e:
        print(f"Database setup failed: {e}")

if __name__ == "__main__":
    print("Installing packages...")
    install_packages()
    print("\nSetting up database...")
    setup_database()
    print("\nSetup complete! Run 'streamlit run main_app.py' to start the application.")