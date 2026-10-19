import os
import json
from conexion_sqlserver import ConexionSqlServer

#JorgeOswaldoRodriguezValades 24420271
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_table(rows, headers):
    if not rows:
        print("  (sin resultados)")
        return
    col_widths = {h: len(h) for h in headers}
    for r in rows:
        for h in headers:
            col_widths[h] = max(col_widths[h], len(str(r.get(h, ''))))
    
    line = "+" + "+".join("-" * (col_widths[h] + 2) for h in headers) + "+"
    print(line)
    header_row = "| " + " | ".join(str(h).ljust(col_widths[h]) for h in headers) + " |"
    print(header_row)
    print(line)
    for r in rows:
        row_str = "| " + " | ".join(str(r.get(h, '')).ljust(col_widths[h]) for h in headers) + " |"
        print(row_str)
    print(line)

class MenuNorthwindSQLServer:

    def mostrar_banner(self):
        print("="*70)
        print("  GESTIÓN NORTHWIND - SQL SERVER ".center(70))
        print("="*70)

    def mostrar_menu(self):
        print("""
        ┌─────────────────────────────────────────────────────┐
        │               MENÚ PRINCIPAL (SQL SERVER)           │
        ├─────────────────────────────────────────────────────┤
        │  1) Consultar / Ver últimos pedidos (SELECT)        │
        │  2) Crear nueva categoría (INSERT)                  │
        │  3) Actualizar nombre de categoría (UPDATE)         │
        │  4) Eliminar categoría (DELETE)                     │
        │  5) Buscar pedidos por cliente (INNER JOIN)         │
        │  0) Salir                                           │
        └─────────────────────────────────────────────────────┘
        """)

    def run(self):
        while True:
            clear()
            self.mostrar_banner()
            self.mostrar_menu()
            try:
                opc = input("  👉 Selecciona una opción [0-5]: ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\nSaliendo...")
                break

            if opc == "1":
                self.op_ver_pedidos()
            elif opc == "2":
                self.op_crear_categoria()
            elif opc == "3":
                self.op_actualizar_categoria()
            elif opc == "4":
                self.op_eliminar_categoria()
            elif opc == "5":
                self.op_bus_ppc()
            elif opc == "0":
                print("\n¡Hasta luego! 👋")
                break
            else:
                print("\n❌ Opción no válida")
            
            input("\nPresiona ENTER para continuar...")

    def op_ver_pedidos(self):
        clear()
        print("\n📦 ÚLTIMOS 10 PEDIDOS (SQL Server) \n")
        try:
            conn = ConexionSqlServer()
            sql = """
            SELECT TOP 10 O.OrderID, C.CompanyName, O.OrderDate, O.ShipCountry 
            FROM Orders O 
            INNER JOIN Customers C ON O.CustomerID = C.CustomerID
            ORDER BY O.OrderDate DESC
            """
            result_json = conn.ejecutar_consulta(sql)
            conn.cerrar_conexion()
            
            result = json.loads(result_json)
            if result.get("estado") and result.get("registros"):
                rows = result["registros"]
                print_table(rows, ["OrderID", "CompanyName", "OrderDate", "ShipCountry"])
            else:
                print("⚠️ No hay registros o ocurrió un error.")
        except Exception as e:
            print(f"Error: {e}")

    def op_crear_categoria(self):
        clear()
        print("\n➕ CREAR NUEVA CATEGORÍA \n")
        nombre = input("Ingresa el nombre de la categoría: ").strip()
        descripcion = input("Ingresa la descripción: ").strip()
        
        if not nombre:
            print("⚠️ El nombre no puede estar vacío.")
            return
            
        try:
            conn = ConexionSqlServer()
            sql = "INSERT INTO Categories (CategoryName, Description) VALUES (?, ?)"
            result_json = conn.ejecutar_consulta(sql, (nombre, descripcion))
            conn.cerrar_conexion()
            
            result = json.loads(result_json)
            if result.get("estado"):
                print(f"\n✅ Categoría creada exitosamente. Filas afectadas: {result.get('registros_afectados')}")
            else:
                print(f"\n❌ Error al crear: {result.get('mensaje')}")
        except Exception as e:
            print(f"Error: {e}")

    def op_actualizar_categoria(self):
        clear()
        print("\n✏️ ACTUALIZAR CATEGORÍA \n")
        try:
            cat_id = int(input("Ingresa el ID de la categoría a actualizar: "))
            nuevo_nombre = input("Ingresa el nuevo nombre: ").strip()
            
            conn = ConexionSqlServer()
            sql = "UPDATE Categories SET CategoryName = ? WHERE CategoryID = ?"
            result_json = conn.ejecutar_consulta(sql, (nuevo_nombre, cat_id))
            conn.cerrar_conexion()
            
            result = json.loads(result_json)
            if result.get("estado") and result.get("registros_afectados", 0) > 0:
                print(f"\n✅ Categoría actualizada correctamente.")
            else:
                print(f"\n⚠️ No se encontró la categoría con ID {cat_id} o no hubo cambios.")
        except ValueError:
            print("⚠️ El ID debe ser un número entero.")
        except Exception as e:
            print(f"Error: {e}")

    def op_eliminar_categoria(self):
        clear()
        print("\n🗑️ ELIMINAR CATEGORÍA \n")
        try:
            cat_id = int(input("Ingresa el ID de la categoría a eliminar: "))
            
            conn = ConexionSqlServer()
            sql = "DELETE FROM Categories WHERE CategoryID = ?"
            result_json = conn.ejecutar_consulta(sql, (cat_id,))
            conn.cerrar_conexion()
            
            result = json.loads(result_json)
            if result.get("estado") and result.get("registros_afectados", 0) > 0:
                print(f"\n✅ Categoría eliminada correctamente.")
            else:
                print(f"\n⚠️ No se encontró ninguna categoría con el ID {cat_id}.")
        except ValueError:
            print("⚠️ El ID debe ser un número entero.")
        except Exception as e:
            print(f"Error: {e}")

    def op_bus_ppc(self):
        clear()
        print("\n🔍 BUSCAR PEDIDOS POR CLIENTE \n")
        customer_id = input("Ingresa el ID del cliente (ej. ALFKI): ").strip().upper()
        if not customer_id:
            print("⚠️ El ID del cliente no puede estar vacío.") 
            return
        try:
            conn = ConexionSqlServer()
            sql = """
            SELECT TOP 10 O.OrderID, C.CompanyName, O.OrderDate, O.ShipCountry 
            FROM Orders O 
            INNER JOIN Customers C ON O.CustomerID = C.CustomerID
            WHERE C.CustomerID = ?
            ORDER BY O.OrderDate DESC
            """
            result_json = conn.ejecutar_consulta(sql, (customer_id,))
            conn.cerrar_conexion()
            
            result = json.loads(result_json)
            if result.get("estado") and result.get("registros"):
                rows = result["registros"]
                print_table(rows, ["OrderID", "CompanyName", "OrderDate", "ShipCountry"])
            else:
                print(f"\n⚠️ No se encontraron pedidos para el cliente: '{customer_id}'")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    menu = MenuNorthwindSQLServer()
    menu.run()