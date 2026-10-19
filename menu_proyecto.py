import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
from psycopg2 import extras

# =============================================================================
# CONFIGURACIÓN DE CONEXIÓN A POSTGRESQL
# =============================================================================
DB_CONFIG = {
    "dbname": "Proyecto",  
    "user": "postgres",             
    "password": "1236",     
    "host": "localhost",
    "port": "5432"
}

# =============================================================================
# VALORES PERMITIDOS PARA LOS TIPOS ENUM EN LA BASE DE DATOS
# =============================================================================
ENUM_OPCIONES = {
    "tipo_cliente": ["Residencial", "PYME", "Corporativo", "Agroindustrial"],
    "categoria": ["Fibra_Optica", "Cable_UTP", "Conector", "Splitter", "Caja_NAP", "Herraje", "Accesorio"],
    "unidad_medida": ["Metro", "Pieza", "Kit", "Bobina", "Caja"],
    "unidad_cobro": ["Por_Evento", "Por_Metro", "Por_Punto", "Por_Hora"],
    "estado_proyecto": ["Borrador", "Cotizado", "Aprobado", "En_Ejecucion", "Cancelado"],
    "longitud_onda_nm": ["1310", "1490", "1550"],
    "categoria_cable": ["Cat5e", "Cat6", "Cat6A", "Cat7"]
}

# =============================================================================
# ESTRUCTURA DE LAS TABLAS DEL PROYECTO "FIBRA EN EL CERRO"
# =============================================================================
TABLAS_SCHEMA = {
    "cliente": {
        "pk": "id_cliente",
        "columnas": ["nombre_cliente", "direccion_instalacion", "telefono", "tipo_cliente"]
    },
    "material": {
        "pk": "id_material",
        "columnas": ["codigo_sku", "nombre_producto", "categoria", "unidad_medida", "costo_unitario", "stock_disponible", "relacion_division", "perdida_insercion_db"]
    },
    "mano_de_obra": {
        "pk": "id_mano_obra",
        "columnas": ["tipo_actividad", "unidad_cobro", "costo_mano_obra"]
    },
    "proyecto": {
        "pk": "id_proyecto",
        "columnas": ["id_cliente", "codigo_proyecto", "nombre_proyecto", "tecnico_responsable", "estado_proyecto"]
    },
    "topologia_ftth": {
        "pk": "id_topologia_ftth",
        "columnas": ["id_proyecto", "id_material_splitter", "distancia_cable_metros", "longitud_onda_nm", "numero_fusiones", "numero_conectores"]
    },
    "presupuesto_optico": {
        "pk": "id_presupuesto_optico",
        "columnas": ["id_topologia_ftth", "atenuacion_total_db", "margen_seguridad_db", "potencia_estimada_rx", "cumple_estandar"]
    },
    "topologia_utp": {
        "pk": "id_topologia_utp",
        "columnas": ["id_proyecto", "cantidad_puntos_red", "categoria_cable", "distancia_promedio_punto", "porcentaje_holgura"]
    },
    "detalle_bom": {
        "pk": "id_detalle_bom",
        "columnas": ["id_proyecto", "id_material", "id_mano_obra", "cantidad_calculada", "precio_unitario_aplicado", "subtotal"]
    },
    "presupuesto_financiero": {
        "pk": "id_presupuesto_financiero",
        "columnas": ["id_proyecto", "costo_total_materiales", "costo_total_mano_obra", "porcentaje_ganancia", "monto_iva", "precio_final_cotizado"]
    },
    "cotizacion": {
        "pk": "id_cotizacion",
        "columnas": ["id_proyecto", "folio_cotizacion", "fecha_emision", "dias_vigencia"]
    }
}


class CRUDApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Sistema CRUD - Proyecto Fibra en el Cerro")
        self.geometry("1100x650")
        self.minsize(900, 500)

        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        self.tabla_activa = None
        self.submenus_visibles = {}

        self._crear_interfaz()

    def obtener_conexion(self):
        """Abre y retorna una conexión a la base de datos PostgreSQL."""
        return psycopg2.connect(**DB_CONFIG)

    def _crear_interfaz(self):
        # Frame Principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # PANEL LATERAL IZQUIERDO
        sidebar_outer = ttk.Frame(main_frame, width=280, relief=tk.RAISED, borderwidth=1)
        sidebar_outer.pack(side=tk.LEFT, fill=tk.Y)
        sidebar_outer.pack_propagate(False)

        lbl_titulo_menu = ttk.Label(
            sidebar_outer, 
            text="📁 TABLAS DEL SISTEMA", 
            font=("Helvetica", 11, "bold"), 
            padding=10, 
            background="#2c3e50", 
            foreground="white",
            anchor="center"
        )
        lbl_titulo_menu.pack(fill=tk.X)

        canvas = tk.Canvas(sidebar_outer, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(sidebar_outer, orient="vertical", command=canvas.yview)
        self.sidebar_frame = ttk.Frame(canvas)

        self.sidebar_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.sidebar_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        for nombre_tabla in TABLAS_SCHEMA.keys():
            btn_tabla = tk.Button(
                self.sidebar_frame,
                text=f"📋 {nombre_tabla.upper()}",
                font=("Helvetica", 10, "bold"),
                bg="#34495e",
                fg="white",
                activebackground="#1abc9c",
                activeforeground="white",
                anchor="w",
                padx=10,
                pady=6,
                relief=tk.FLAT,
                command=lambda t=nombre_tabla: self.toggle_submenu(t)
            )
            btn_tabla.pack(fill=tk.X, pady=(2, 0), padx=2)

            sub_frame = ttk.Frame(self.sidebar_frame, padding=(15, 2, 5, 5))
            
            btn_consultar = ttk.Button(sub_frame, text="🔍 Consultar / Listar", command=lambda t=nombre_tabla: self.accion_consultar(t))
            btn_insertar = ttk.Button(sub_frame, text="➕ Añadir Registro", command=lambda t=nombre_tabla: self.accion_insertar(t))
            btn_modificar = ttk.Button(sub_frame, text="✏️ Modificar Seleccionado", command=lambda t=nombre_tabla: self.accion_modificar(t))
            btn_eliminar = ttk.Button(sub_frame, text="🗑️ Eliminar Seleccionado", command=lambda t=nombre_tabla: self.accion_eliminar(t))

            btn_consultar.pack(fill=tk.X, pady=2)
            btn_insertar.pack(fill=tk.X, pady=2)
            btn_modificar.pack(fill=tk.X, pady=2)
            btn_eliminar.pack(fill=tk.X, pady=2)

            self.submenus_visibles[nombre_tabla] = {
                "frame": sub_frame,
                "visible": False
            }

        # PANEL CENTRAL DERECHO
        content_frame = ttk.Frame(main_frame, padding=10)
        content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.lbl_cabecera = ttk.Label(
            content_frame, 
            text="Selecciona una tabla en el menú lateral para operar", 
            font=("Helvetica", 14, "bold")
        )
        self.lbl_cabecera.pack(anchor="w", pady=(0, 10))

        tree_container = ttk.Frame(content_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(tree_container, show="headings")
        vsb = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)

        self.lbl_status = ttk.Label(self, text="Estado: Listo", relief=tk.SUNKEN, anchor="w", padding=5)
        self.lbl_status.pack(side=tk.BOTTOM, fill=tk.X)

    def toggle_submenu(self, nombre_tabla):
        info = self.submenus_visibles[nombre_tabla]
        if info["visible"]:
            info["frame"].pack_forget()
            info["visible"] = False
        else:
            for t, data in self.submenus_visibles.items():
                data["frame"].pack_forget()
                data["visible"] = False
            
            info["frame"].pack(fill=tk.X)
            info["visible"] = True
            
        self.tabla_activa = nombre_tabla
        self.accion_consultar(nombre_tabla)

    def accion_consultar(self, tabla):
        self.tabla_activa = tabla
        self.lbl_cabecera.config(text=f"Tabla Actual: '{tabla.upper()}'")
        self.lbl_status.config(text=f"Consultando la tabla {tabla}...")

        self.tree["columns"] = ()
        for item in self.tree.get_children():
            self.tree.delete(item)

        pk = TABLAS_SCHEMA[tabla]["pk"]
        cols = [pk] + TABLAS_SCHEMA[tabla]["columnas"]

        self.tree["columns"] = cols
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=130, anchor="center")

        try:
            conn = self.obtener_conexion()
            cursor = conn.cursor(cursor_factory=extras.DictCursor)
            query = f"SELECT {', '.join(cols)} FROM {tabla} ORDER BY {pk} ASC;"
            cursor.execute(query)
            registros = cursor.fetchall()
            conn.close()

            for reg in registros:
                valores = [reg[col] for col in cols]
                self.tree.insert("", tk.END, values=valores)

            self.lbl_status.config(text=f"Consulta exitosa en '{tabla}'. {len(registros)} registro(s) encontrado(s).")
        except Exception as e:
            messagebox.showerror("Error de Base de Datos", f"No se pudo consultar la tabla:\n{e}")
            self.lbl_status.config(text="Error durante la consulta.")

    def accion_insertar(self, tabla):
        cols = TABLAS_SCHEMA[tabla]["columnas"]
        dialog = FormularioDialog(self, title=f"Añadir Registro a {tabla}", columnas=cols)
        self.wait_window(dialog)

        if dialog.resultado:
            datos = dialog.resultado
            columnas_sql = ", ".join(datos.keys())
            valores_sql = ", ".join(["%s"] * len(datos))
            query = f"INSERT INTO {tabla} ({columnas_sql}) VALUES ({valores_sql});"

            try:
                conn = self.obtener_conexion()
                cursor = conn.cursor()
                cursor.execute(query, list(datos.values()))
                conn.commit()
                conn.close()
                messagebox.showinfo("Éxito", "Registro añadido correctamente.")
                self.accion_consultar(tabla)
            except Exception as e:
                messagebox.showerror("Error al insertar", f"No se pudo insertar el registro:\n{e}")

    def accion_modificar(self, tabla):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Por favor, selecciona un registro de la tabla para modificar.")
            return

        item = self.tree.item(seleccion[0])
        valores = item["values"]
        pk_nombre = TABLAS_SCHEMA[tabla]["pk"]
        cols = TABLAS_SCHEMA[tabla]["columnas"]
        
        val_pk = valores[0]
        valores_dict = dict(zip(cols, valores[1:]))

        dialog = FormularioDialog(self, title=f"Modificar {tabla} ({pk_nombre}={val_pk})", columnas=cols, datos_iniciales=valores_dict)
        self.wait_window(dialog)

        if dialog.resultado:
            datos = dialog.resultado
            set_clause = ", ".join([f"{col} = %s" for col in datos.keys()])
            query = f"UPDATE {tabla} SET {set_clause} WHERE {pk_nombre} = %s;"

            try:
                conn = self.obtener_conexion()
                cursor = conn.cursor()
                cursor.execute(query, list(datos.values()) + [val_pk])
                conn.commit()
                conn.close()
                messagebox.showinfo("Éxito", "Registro actualizado correctamente.")
                self.accion_consultar(tabla)
            except Exception as e:
                messagebox.showerror("Error al modificar", f"No se pudo actualizar el registro:\n{e}")

    def accion_eliminar(self, tabla):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Por favor, selecciona un registro de la tabla para eliminar.")
            return

        item = self.tree.item(seleccion[0])
        val_pk = item["values"][0]
        pk_nombre = TABLAS_SCHEMA[tabla]["pk"]

        confirmar = messagebox.askyesno(
            "Confirmar eliminación", 
            f"¿Estás seguro de eliminar el registro con {pk_nombre} = {val_pk} de la tabla '{tabla}'?"
        )

        if confirmar:
            query = f"DELETE FROM {tabla} WHERE {pk_nombre} = %s;"
            try:
                conn = self.obtener_conexion()
                cursor = conn.cursor()
                cursor.execute(query, [val_pk])
                conn.commit()
                conn.close()
                messagebox.showinfo("Éxito", "Registro eliminado correctamente.")
                self.accion_consultar(tabla)
            except Exception as e:
                messagebox.showerror("Error al eliminar", f"No se pudo eliminar el registro:\n{e}")


# =============================================================================
# FORMULARIO DINÁMICO (SOPORTA DESPLEGABLES PARA ENUMS)
# =============================================================================
class FormularioDialog(tk.Toplevel):
    def __init__(self, parent, title, columnas, datos_iniciales=None):
        super().__init__(parent)
        self.title(title)
        self.columnas = columnas
        self.datos_iniciales = datos_iniciales or {}
        self.resultado = None

        self.entries = {}
        self._crear_formulario()
        self.grab_set()
        
    def _crear_formulario(self):
        frame = ttk.Frame(self, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)

        for idx, col in enumerate(self.columnas):
            lbl = ttk.Label(frame, text=f"{col}:", font=("Helvetica", 9, "bold"))
            lbl.grid(row=idx, column=0, sticky="e", pady=4, padx=5)

            # Si la columna es tipo ENUM, creamos una lista desplegable (Combobox)
            if col in ENUM_OPCIONES:
                entry = ttk.Combobox(frame, values=ENUM_OPCIONES[col], state="readonly", width=33)
                if col in self.datos_iniciales and self.datos_iniciales[col]:
                    entry.set(str(self.datos_iniciales[col]))
                elif ENUM_OPCIONES[col]:
                    entry.current(0)  # Selecciona el primer valor por defecto
            else:
                entry = ttk.Entry(frame, width=35)
                if col in self.datos_iniciales and self.datos_iniciales[col] is not None:
                    entry.insert(0, str(self.datos_iniciales[col]))

            entry.grid(row=idx, column=1, sticky="w", pady=4, padx=5)
            self.entries[col] = entry

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=len(self.columnas), column=0, columnspan=2, pady=(15, 0))

        btn_guardar = ttk.Button(btn_frame, text="💾 Guardar", command=self.guardar)
        btn_cancelar = ttk.Button(btn_frame, text="❌ Cancelar", command=self.destroy)

        btn_guardar.pack(side=tk.LEFT, padx=5)
        btn_cancelar.pack(side=tk.LEFT, padx=5)

    def guardar(self):
        datos = {}
        for col, entry in self.entries.items():
            valor = entry.get().strip()
            if valor == "":
                datos[col] = None
            else:
                datos[col] = valor
        self.resultado = datos
        self.destroy()


if __name__ == "__main__":
    app = CRUDApp()
    app.mainloop()