import pymysql
from pymysql import connections

class ConnectionPool:
    def __init__(self, pool_size, **kwargs):
        self.pool_size = pool_size
        self.connection_params = kwargs
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

# Parámetros de conexión
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '12345',
    'database': 'entidad_bancaria',
}

# Crear un pool de conexiones
pool = ConnectionPool(pool_size=1, **db_config)

# Obtener una conexión
connection = pool.get_connection()
print("Conexión exitosa")

# Liberar la conexión
pool.release_connection(connection)

