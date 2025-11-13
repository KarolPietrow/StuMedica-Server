import sqlite3

import auth


class UserDatabase:
    def __init__(self, db_file: str = "users.db"):
        self.db_file = db_file
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                age INTEGER,
                account_type TEXT NOT NULL CHECK(account_type IN ('patient', 'doctor')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_email ON users(email)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_account_type ON users(account_type)
            """)

            conn.commit()
    def create_user(self, name: str, email: str, password: str, age: int, account_type: str):
        password_hash = auth.get_password_hash(password)
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                print("Trying to create user")
                cursor.execute("""
                    INSERT INTO users (name, email, password_hash, age, account_type)
                    VALUES (?, ?, ?, ?, ?)
                """, (name, email, password_hash, age, account_type))
                print("Trying to commit")
                conn.commit()
                print("User created successfully")
                return True, f"User {name} created successfully with ID {cursor.lastrowid}"
        except sqlite3.IntegrityError:
            print("User already exists")
            return False, "Email already exists"
        except Exception as e:
            print(f"Error creating user: {str(e)}")
            return False, f"Error creating user {str(e)}"

