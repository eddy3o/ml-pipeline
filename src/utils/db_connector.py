import sqlite3

def get_db_connection(db_path):
    return sqlite3.connect(db_path)

def save_dataframe_to_table(df, table_name, db_path):
    conn = get_db_connection(db_path)
    try:
        df.to_sql(table_name, conn, if_exists="replace", index=False)
    finally:
        conn.close()

def run_migrations(db_path):
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS adoption_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            edad INTEGER,
            genero_adoptante TEXT,
            tipo_vivienda TEXT,
            genero_mascota TEXT,
            fecha_adopcion TEXT,
            integrantes_familia INTEGER,
            perros INTEGER,
            gatos INTEGER
        )
        """)
        conn.commit()
    finally:
        conn.close()