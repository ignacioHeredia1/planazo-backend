import sqlite3

def update_db():
    conn = sqlite3.connect('planify.db')
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE planes ADD COLUMN permite_reservas BOOLEAN DEFAULT 0")
        conn.commit()
        print("Columna 'permite_reservas' añadida con exito.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("La columna ya existe.")
        else:
            print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    update_db()
