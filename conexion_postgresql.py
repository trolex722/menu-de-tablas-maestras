import psycopg2
import json

#JORGE OSWALDO RODRIGUEZ VALADES 24420271
class ConexionPostgresql:
    
    def __init__(self):
        self.HOST = "localhost"
        self.DATABASE_NAME = "Northwind"
        self.USER = "postgres"
        self.PASSWORD = "1236"
        self.PORT = 5432             # Puerto por defecto en PostgreSQL
        
        self.CNX = None              # Gestionar la conexión
        self.CURSOR = None           # Gestionar las consultas
        
    def crear_conexion(self):
        """Crea la conexión a la base de datos PostgreSQL"""
        try:
            self.CNX = psycopg2.connect(
                host=self.HOST,
                database=self.DATABASE_NAME,
                user=self.USER,
                password=self.PASSWORD,
                port=self.PORT
            )
            self.CURSOR = self.CNX.cursor()
            print(f"Conectado al servidor PostgreSQL: {self.HOST}")
            return self.CNX
        except Exception as e:
            print(f"Error al conectarse al servidor {self.HOST} de base de datos")
            print(e)
            self.CNX = None
            self.CURSOR = None
            return None
        
    def ejecutar_consulta(self, sql, parametros=None):
        """Metodo para realizar consultas a la base de datos y retornar JSON"""
        try:
            # 1. Verificar o restablecer la conexión
            if self.CNX is None or self.CNX.closed != 0:
                if self.crear_conexion() is None:
                    return json.dumps(
                        {
                            "estado": False,
                            "mensaje": "no fue posible conectarse a la base de datos"
                        },
                        ensure_ascii=False
                    )

            # 2. Ejecutar la consulta con o sin parámetros
            if parametros:
                self.CURSOR.execute(sql, parametros)
            else:
                self.CURSOR.execute(sql)
                    
            # 3. Identificar el tipo de operación
            tipo = sql.strip().split()[0].upper()

            # --- Consultas de Lectura (SELECT) ---
            if tipo == "SELECT":
                # Extraer títulos de columnas
                columnas = [columna[0] for columna in self.CURSOR.description]
                
                # Obtener los registros
                registros = self.CURSOR.fetchall()
                
                # Mapear cada fila a un diccionario {columna: valor}
                resultados = []
                for registro in registros:
                    fila = {}
                    for i, valor in enumerate(registro):
                        fila[columnas[i]] = valor
                    resultados.append(fila)

                return json.dumps(
                    {
                        "estado": True,
                        "tipo": "SELECT",
                        "registros": resultados
                    },
                    ensure_ascii=False,
                    default=str  # Serializa tipos como datetime o Decimal a String
                )

            # --- Consultas de Escritura (INSERT, UPDATE, DELETE) ---
            else:
                self.CNX.commit()  # Guardar cambios permanentemente
                return json.dumps(
                    {
                        "estado": True,
                        "tipo": tipo,
                        "registros_afectados": self.CURSOR.rowcount
                    },
                    ensure_ascii=False
                )

        except Exception as e:
            if self.CNX:
                self.CNX.rollback()  # Revertir transacción si ocurre un error
            return json.dumps(
                {
                    "estado": False,
                    "mensaje": f"Error al ejecutar la consulta: {str(e)}"
                },
                ensure_ascii=False
            )
        
    def cerrar_conexion(self):
        """Método para cerrar la conexión a la base de datos"""
        try:
            if self.CURSOR:
                self.CURSOR.close()
                self.CURSOR = None
            if self.CNX and self.CNX.closed == 0:
                self.CNX.close()
                self.CNX = None
            print(f"Se ha cerrado la conexión con el servidor: {self.HOST}")
            return True
        except Exception as e:
            print(f"Error al desconectarse de la base de datos")
            print(e)
            return False


if __name__ == '__main__':
    cnn = ConexionPostgresql()
    res_json = cnn.ejecutar_consulta("""
        select C.company_name, O.order_id, P.product_name, OD.quantity, OD.unit_price, OD.discount,
        (OD.quantity * OD.unit_price * (1 - OD.discount)) as subtotal
        from customers C
        inner join orders O on C.customer_id = O.customer_id
        inner join order_details OD on O.order_id = OD.order_id
        inner join products P on OD.product_id = P.product_id
        where O.order_id = 10248;
    """)
    result = json.loads(res_json)
    if result.get("estado"):
        for r in result["registros"]:
            print(r) 
    cnn.cerrar_conexion()