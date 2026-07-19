from datetime import timedelta

MYSQL_HOST = '127.0.0.1'
MYSQL_PORT = 3306
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'Leto2026Deploy#'
MYSQL_DB = 'leto_user_db'

DB_URI = f"mysql+asyncmy://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8mb4"

DATA_CENTER_ID = 0
WORKER_ID = 0

JWT_SECRET_KEY = "c7f9a2e1b84d6c3f91e7ab2450d8c6fe4a19b7d2"
JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=15)

CONSUL_HOST = "127.0.0.1"
CONSUL_PORT = 8500

SERVICE_NAME = "auth_service"