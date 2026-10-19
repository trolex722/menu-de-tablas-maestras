import os
from conexion_postgresql import ConexionPostgresql
import json

# -------------------- UTILIDADES DE CONSOLA --------------------
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_table(rows, headers):
    if not rows:
        print("  (sin resultados)")
        return
    # Ancho de columnas
    col_widths = {h: len(h) for h in headers}
    for r in rows:
        for h in headers:
            col_widths[h] = max(col_widths[h], len(str(r.get(h, ''))))
    
    # Línea superior
    line = "+" + "+".join("-" * (col_widths[h] + 2) for h in headers) + "+"
    print(line)
    header_row = "| " + " | ".join(str(h).ljust(col_widths[h]) for h in headers) + " |"
    print(header_row)
    print(line)
    for r in rows:
        row_str = "| " + " | ".join(str(r.get(h, '')).ljust(col_widths[h]) for h in headers) + " |"
        print(row_str)
    print(line)

# -------------------- CLASE MENU PRINCIPAL --------------------
class MenuNorthwind:
    # def __init__(self, repo: NorthwindRepository):
    #    self.repo = repo

    def mostrar_banner(self):
        print("="*70)
        print("  ███╗   ██╗ ██████╗ ██████╗ ████████╗██╗  ██╗██╗    ██╗██╗███╗   ██╗██████╗ ".center(70))
        print("  ████╗  ██║██╔═══██╗██╔══██╗╚══██╔══╝██║  ██║██║    ██║██║████╗  ██║██╔══██╗".center(70))
        print("  ██╔██╗ ██║██║   ██║██████╔╝   ██║   ███████║██║ █╗ ██║██║██╔██╗ ██║██║  ██║".center(70))
        print("  ██║╚██╗██║██║   ██║██╔══██╗   ██║   ██╔══██║██║███╗██║██║██║╚██╗██║██║  ██║".center(70))
        print("  ██║ ╚████║╚██████╔╝██║  ██║   ██║   ██║  ██║╚███╔███╔╝██║██║ ╚████║██████╔╝".center(70))
        print("="*70)
        print("           GESTOR DE PEDIDOS - CONSOLA ".center(70))
        print("="*70)

    def mostrar_menu(self):
        print("""
        ┌─────────────────────────────────────────────────────┐
        │                   MENÚ PRINCIPAL                    │
        ├─────────────────────────────────────────────────────┤
        │  1) Ver últimos 10 pedidos (INNER JOIN)             │
        │  2) Ver detalle de un pedido                        │
        │  3) Crear nuevo pedido                              │
        │  4) Eliminar pedido                                 │
        │  5) Buscar pedidos por cliente (LEFT JOIN)          │
        │  6) Clientes que nunca han pedido (LEFT JOIN+NULL)  │
        │  7) Productos nunca vendidos (LEFT JOIN+NULL)       │
        │  8) Estadísticas y TOP clientes                     │
        │  9) Ver 10 consultas de ejemplo (INNER/LEFT/RIGHT)  │
        │  0) Salir                                           │
        └─────────────────────────────────────────────────────┘
        """)

    def run(self):
        while True:
            clear()
            self.mostrar_banner()
            self.mostrar_menu()
            try:
                opc = input("  👉 Selecciona una opción [0-9]: ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\nSaliendo...")
                break

            if opc == "1":
                self.op_ver_pedidos()
            if opc == "5":
                self.op_bus_ppc()
            elif opc == "0":
                print("\n¡Hasta luego! 👋")
                break
            else:
                print("\n❌ Opción no válida")
            
            input("\nPresiona ENTER para continuar...")

    # --- OPERACIONES ---
    def op_ver_pedidos(self):
        clear()
        print("\n📦 ÚLTIMOS 10 PEDIDOS \n")
        try:
            conn=ConexionPostgresql()
            sql="""select O.order_id, C.company_name, O.order_date, ship_country 
            from orders O 
            inner join customers C on O.customer_id=C.customer_id
            order by O.order_date desc
            limit %(limite)s
            """
            result=conn.ejecutar_consulta(sql, {"limite":10})
            conn.cerrar_conexion()
            rows = result["registros"]
            print_table(rows, ["order_id", "company_name", "fecha", "pais"])
        except Exception as e:
            print(f"Error: {e}")
            
    def op_bus_ppc(self):
        clear()
        print("\n PEDIDOS POR CLIENTE \n")
        customer_id = input("Ingresa el ID del cliente (ej. ALFKI): ").strip().upper()
        if not customer_id:
            print("⚠️ El ID del cliente no puede estar vacío.") 
            return
        try:
            conn = ConexionPostgresql()
            sql = """
            select O.order_id, C.company_name, O.order_date, O.ship_country 
            from orders O 
            inner join customers C on O.customer_id = C.customer_id
            where C.customer_id = %(customer_id)s
            order by O.order_date desc
            limit %(limite)s;
            """
            parametros = {
                "customer_id": customer_id,
                "limite": 10
            }
            result_json = conn.ejecutar_consulta(sql, parametros)
            conn.cerrar_conexion()
            result = json.loads(result_json)
            if result.get("estado") and result.get("registros"):
                rows = result["registros"]
                print_table(rows, ["order_id", "company_name", "order_date", "ship_country"])
            else:
                print(f"\n No se encontraron pedidos para el cliente: '{customer_id}'")
        except Exception as e:
            print(f"Error: {e}")
            


# -------------------- MAIN --------------------
if __name__ == "__main__":
    m = MenuNorthwind()
    m.run()
