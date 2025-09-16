import mariadb

USER = "inventario"
PASSWORD = "123456"
HOST = "localhost"
DATABASE = "inventario"

try:
	conn = mariadb.connect(user=USER, password=PASSWORD, host=HOST, database=DATABASE)
	cursor = conn.cursor()
except mariadb.Error as e:
	print(f"Error conectando a MariaDB: {e}")