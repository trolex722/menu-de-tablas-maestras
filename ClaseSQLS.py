import pyodbc

class SQLServerDB:
    def __init__(self, server, database, user, password, driver="{ODBC Driver 17 for SQL Server}"):
        self.server = server
        self.database = database
        self.user = user
        self.password = password
        self.driver = driver
        self.conexion = None

    def Crea_conexion(self):
        """Crea y regresa la conexión a la base de datos SQL Server."""
        try:
            cadena_conexion = (
                f"DRIVER={self.driver};"
                f"SERVER={self.server};"
                f"DATABASE={self.database};"
                f"UID={self.user};"
                f"PWD={self.password};"
            )
            self.conexion = pyodbc.connect(cadena_conexion)
            return self.conexion
        except Exception as e:
            print(f"Error al conectar a SQL Server: {e}")
            return None

    def ejecutar_consulta(self, consulta_sql):
        """
        Ejecuta una consulta SQL.
        - SELECT: Regresa los datos recuperados como una lista de tuplas.
        - INSERT/UPDATE/DELETE: Regresa el número de registros afectados.
        """
        if not self.conexion:
            if not self.Crea_conexion():
                return None

        try:
            cursor = self.conexion.cursor()
            cursor.execute(consulta_sql)
            
            # Verificar si la consulta regresa resultados (SELECT)
            if cursor.description is not None:
                resultados = cursor.fetchall()
                cursor.close()
                return resultados
            else:
                # Consultas de modificación (INSERT, UPDATE, DELETE)
                filas_afectadas = cursor.rowcount
                self.conexion.commit()
                cursor.close()
                return filas_afectadas

        except Exception as e:
            print(f"Error al ejecutar la consulta en SQL Server: {e}")
            if self.conexion:
                self.conexion.rollback()
            return None

    def Cerrar_Conexion(self):
        """Cierra la conexión y regresa True si se cerró satisfactoriamente."""
        try:
            if self.conexion:
                self.conexion.close()
                self.conexion = None
                return True
            return False
        except Exception as e:
            print(f"Error al cerrar la conexión: {e}")
            return False