import psycopg2

DB_CONFIG = {
    "dbname": "musicdb",
    "user": "admin",
    "password": "test",
    "host": "localhost",
    "port": "5432",
}

try:
    conn = psycopg2.connect(**DB_CONFIG)
    print("подключение к базе данных успешно!")
    conn.close()
except Exception as e:
    print(f"ошибка подключения: {e}")
