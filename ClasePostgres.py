import psycopg2
from psycopg2 import Extras

class PostgresDB:
    def __init__(self, host, database, user, password, port=5432):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port
        self.conexion = None

    def Crea_conexion(self):
        """Crea y regresa la conexión a la base de datos PostgreSQL."""
        try:
            self.conexion = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port
            )
            return self.conexion
        except Exception as e:
            print(f"Error al conectar a PostgreSQL: {e}")
            return None

    def ejecutar_consulta(self, consulta_sql):
        """
        Ejecuta una consulta SQL.
        - SELECT: Regresa los datos recuperados como una lista de tuplas.
        - INSERT/UPDATE/DELETE: Regresa el número de registros afectados.
        """
        if not self.conexion or self.conexion.closed != 0:
            if not self.Crea_conexion():
                return None

        try:
            cursor = self.conexion.cursor()
            cursor.execute(consulta_sql)
            
            # Verificar si la consulta regresa filas (SELECT)
            if cursor.description is not None:
                resultados = cursor.fetchall()
                cursor.close()
                return resultados
            else:
                # Consultas de modificación (INSERT, UPDATE, DELETE)
                self.conexion.commit()
                filas_afectadas = cursor.rowcount
                cursor.close()
                return filas_afectadas

        except Exception as e:
            print(f"Error al ejecutar la consulta en PostgreSQL: {e}")
            if self.conexion:
                self.conexion.rollback()
            return None

    def Cerrar_Conexion(self):
        """Cierra la conexión y regresa True si se cerró satisfactoriamente."""
        try:
            if self.conexion and self.conexion.closed == 0:
                self.conexion.close()
                return True
            return False
        except Exception as e:
            print(f"Error al cerrar la conexión: {e}")
            return False