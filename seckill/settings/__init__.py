MYSQL_HOST = '127.0.0.1'
MYSQL_PORT = 3306
MYSQL_USER = 'root'
MYSQL_PASSWORD = '12345678'
MYSQL_DB = 'leto_seckill_db'

DB_URI = f"mysql+asyncmy://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8mb4"

DATA_CENTER_ID = 0
WORKER_ID = 0

KAFKA_BROKER_SERVER = "192.168.10.110:9092"

ALIPAY_APP_ID = "9021000163616188"
ALIPAY_RETURN_URL = "http://localhost:5173/#/payment_result"
ALIPAY_BASE_URL = "https://openapi-sandbox.dl.alipaydev.com/gateway.do"
ALIPAY_NOTIFY_URL = "http://pe72cdce.natappfree.cc/seckill/post_payment_result"

CONSUL_HOST = "192.168.10.110"
CONSUL_PORT = 8500

SERVICE_NAME = "seckill_service"