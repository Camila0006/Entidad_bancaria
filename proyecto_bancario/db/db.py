import os
import dj_database_url
import pymysql
from pymysql import connections

class ConnectionPool:
    def __init__(self, pool_size, **kwargs):
        self.pool_size = pool_size
        self.connection_params = {
            'host': kwargs['HOST'],
            'user': kwargs['USER'],
            'password': kwargs['PASSWORD'],
            'database': kwargs['NAME'],
        }
        self.connections = []

        # Crear conexiones iniciales en el pool
        for _ in range(pool_size):
            try:
                connection = pymysql.connect(**self.connection_params)
                self.connections.append(connection)
            except pymysql.MySQLError as e:
                print(f"Error al crear una conexión: {e}")
                raise

    def get_connection(self):
        if not self.connections:
            raise Exception("No hay más conexiones disponibles en el pool")
        return self.connections.pop()

    def release_connection(self, connection):
        if len(self.connections) < self.pool_size:
            self.connections.append(connection)
        else:
            connection.close()

# Obtener la URL de la base de datos de las variables de entorno
database_url = os.getenv('DATABASE_URL')

if not database_url:
    raise Exception("DATABASE_URL no está configurada en las variables de entorno.")

# Convertir la URL a un diccionario
db_config = dj_database_url.parse(database_url)

# Crear un pool de conexiones
pool = ConnectionPool(pool_size=1, **db_config)

# Obtener una conexión
connection = pool.get_connection()
print("Conexión exitosa")

# Liberar la conexión
pool.release_connection(connection)
